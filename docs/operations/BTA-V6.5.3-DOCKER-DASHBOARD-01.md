# BTA-V6.5.3-DOCKER-DASHBOARD-01

**Status:** Deferred.

On November 20, 2026, selecting Dashboard from the Windows Docker tray launched the Docker Desktop UI process but no window appeared. Docker’s Linux engine reported running and successfully built and tested the V6.5.3 Scripture image. Recent dashboard logs did not establish the cause.

This issue does not block command-line image builds or the BTA dev browser test. Recheck Dashboard startup and renderer diagnostics during a separate workstation maintenance window. A full Docker Desktop restart can interrupt running containers, so schedule it independently of BTA validation.
