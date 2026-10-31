**1. CONFIRMED AT minor.** Steps 2 and 3 use "the change ticket" and `<id>` as if one already exists, and nothing says how to get one. An on-call engineer will know the change process, and no command or result depends on it, so it isn't blocking.

**2. CONFIRMED AT minor.** Layout gives a full URL for the Vendor Console but only the dashboard and panel names for Grafana. Both names are specific enough to find the panel.

**3. CONFIRMED AT blocking.** Step 7 ends with `&& echo OK` and says nothing about a missing OK. The service is stopped at that point, and the Rollback trigger covers only a failed start and lag. The engineer can't tell whether to fix the file, restore the backup or page someone.

**4. CONFIRMED AT misleading.** Step 9 is "Verify the rotation worked." with no command and no expected result. An engineer could judge it "worked" because the unit is active, even if auth is failing. Step 10's lag panel only partly covers this.

**5. CONFIRMED AT misleading.** "Acceptable" and "recover" have no number, and the 15 minutes has no start point. Notes gives 2 to 8 s as normal and 60 s as the alert threshold, so the engineer can work out a range. They could still continue at 50 s or roll back needlessly. It isn't blocking, since Notes supplies candidate numbers.

**6. CONFIRMED AT misleading.** Step 11 contains the literal "OWNER TO SET" placeholder, so no deletion time exists. The engineer is told not to delete now and given no later trigger. The old key then either stays live, or gets deleted at the end of the run, which removes the rollback path.

**7. CONFIRMED AT misleading.** The trigger line omits a failed step 7. Step 13 restarts the service but doesn't check it recovered, doesn't announce the rollback, and doesn't revoke the new key in the Vendor Console. A rollback that silently fails would look finished once step 14's page is sent.

**8. CONFIRMED AT misleading.** Step 11 says that for a compromised key you delete the old key now and note that rollback is unavailable. Step 13 is unconditional, says the old key "stays valid for 24 hours", and restores the backup. After that deletion it would restore a dead key and leave the service failing to authenticate. The Rollback section never mentions the exception.
