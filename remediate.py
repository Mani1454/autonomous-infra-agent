import psutil
import os
from datetime import datetime


class ActionManager:
    """
    Handles self-healing remediation actions with full audit logging.

    Provides safe process termination and maintains an append-only
    audit trail of every action taken by the agent.
    """

    AUDIT_LOG_PATH = os.path.join(os.path.dirname(__file__), "audit.log")

    def kill_process(self, pid: int) -> str:
        """
        Safely terminates a process by its PID.

        First attempts a graceful termination (SIGTERM). If the process
        does not exit within 5 seconds, escalates to a forced kill (SIGKILL).

        Args:
            pid: The process ID to terminate.

        Returns:
            A status string indicating the result of the operation.
        """
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.terminate()  # Graceful SIGTERM
            proc.wait(timeout=5)

            status = f"✅ Process '{proc_name}' (PID {pid}) terminated successfully."
            self.log_action("kill_process", pid, status)
            return status

        except psutil.NoSuchProcess:
            status = f"⚠️ PID {pid} no longer exists — it may have already exited."
            self.log_action("kill_process", pid, status)
            return status

        except psutil.AccessDenied:
            status = f"🔒 Permission denied: cannot terminate PID {pid}. Run as administrator."
            self.log_action("kill_process", pid, status)
            return status

        except psutil.TimeoutExpired:
            # Graceful termination timed out — force kill
            try:
                proc.kill()
                status = f"⚠️ Graceful termination timed out. Force-killed PID {pid}."
                self.log_action("kill_process", pid, status)
                return status
            except Exception as e:
                status = f"❌ Force-kill failed for PID {pid}: {e}"
                self.log_action("kill_process", pid, status)
                return status

        except Exception as e:
            status = f"❌ Unexpected error terminating PID {pid}: {e}"
            self.log_action("kill_process", pid, status)
            return status

    def log_action(self, action_type: str, pid: int, status: str) -> None:
        """
        Appends a timestamped audit record to audit.log.

        Args:
            action_type: The type of action performed (e.g., 'kill_process').
            pid: The target process ID.
            status: The result/status message of the action.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] ACTION={action_type} | PID={pid} | STATUS={status}\n"

        with open(self.AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
