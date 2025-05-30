# Garmin Activity Merge – Resume Notes

## Purpose
This project manages a personal Garmin activity database using a custom Python script to cleanly merge CSV exports from Garmin Connect into a slimmed-down SQLite database, with normalization of activity types and deduplication logic.

## Current Files
- **Database:** `garmin_activities.sqlite`
- **Merge Script:** `garmin_merge.py`
- **Example CSV:** `Activities.csv` (Garmin Connect export format)

## Current Database Schema
| Field           | Type     | Notes                                  |
|----------------|----------|----------------------------------------|
| activity_type   | TEXT     | To be normalized to canonical values   |
| date            | TEXT     | ISO 8601 date with time (e.g. 2025-05-26 18:07:10) |
| title           | TEXT     | Original activity title from Garmin    |
| distance        | REAL     | In miles                               |
| calories        | INTEGER  |                                        |
| time            | INTEGER  | Duration in seconds                    |
| avg_hr          | INTEGER  |                                        |
| max_hr          | INTEGER  |                                        |
| total_ascent    | INTEGER  | In feet or meters depending on Garmin export |

## Canonical Activity Types (Planned for Normalization)
Only these values should remain after mapping:

- `running`
- `cycling`
- `mountain biking`
- `walking`
- `rowing`
- `backcountry skiing`
- `resort skiing`
- `strength training`
- `other`

Any activity not matching or mapped to the above will default to `other`. Titles remain unchanged.

## Outstanding Tasks (When Resuming)
- Implement normalization of activity types in `garmin_merge.py`
- Ensure CSV merges only insert or update valid entries
- Optionally review titles of activities mapped to `other`
- Optionally implement logging for unknown/unsupported activity types

## Instructions to Resume
When you're ready:
1. Upload:
   - `garmin_activities.sqlite`
   - `garmin_merge.py`
   - A sample or test `Activities.csv`
2. Paste this file into the chat to reestablish context.
3. Say: **"Let's resume the Garmin merge normalization project."**

I’ll pick up from there.
