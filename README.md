# Garmin
Tools for sports activity data management and analysis

The merge tool is meant to take a csv from Garmin Connect and add its activities to an SQLite database. The cleaner tool is just for cleaning up the db if that becomes necessary.
To Use:
    1. Log in to Garmin connect on the web.
    2. Select Activities / All Activities from left menu.
    3. Click “Export CSV” (upper right) and save the file somewhere.
    4. run python3 garmin_merge.py newactivites.csv garmin_activities.sqlite

newactivities.csv should have just showed up in /Downloads, and garmin_activities.sqlite should be in the same director as the merge tool.
