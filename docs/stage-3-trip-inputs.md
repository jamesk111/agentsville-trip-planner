# Stage 3: Trip inputs and available data

The notebook now validates the trip details and retrieves the data for each day. This stage runs locally and makes no model requests.

## The sample trip

- Travelers: Yuri, Hiro.
- Destination: AgentsVille.
- Dates: 2025-06-10 through 2025-06-12, including both dates.
- Budget: 130 fictional currency units.

## What validation does

VacationInfo turns the date strings into Python dates and each traveler into a Traveler object. Interests must match the supplied Interest enum. A trip needs travelers, nonblank names and destination, at least one interest per traveler, and a whole nonnegative budget. Departure cannot precede arrival. Unknown field names are rejected so a typo does not disappear silently.

A same-day trip and a zero budget are valid inputs. Whether available activities can satisfy that budget is a planning question.

The model describes a trip independently of this dataset. The lookup cells report a clear error if the city or any requested day has no supplied data. The supplied dataset covers AgentsVille from June 10 through June 15, 2025.

## Retrieved weather and activity counts

| Date | Forecast | Temperature | Available activities |
| --- | --- | --- | --- |
| 2025-06-10 | clear | 31 C | 4 |
| 2025-06-11 | partly cloudy | 34 C | 4 |
| 2025-06-12 | thunderstorm | 28 C | 4 |

Total: 3 forecasts and 12 activities. These are the available options. The planner will choose from them in the next stage.

## Available activities

| Date | Time | Activity | Price |
| --- | --- | --- | --- |
| 2025-06-10 | 09:00–11:00 | FutureTech Breakfast Meet-Up | 20 |
| 2025-06-10 | 12:00–13:30 | Serve & Savor: Tennis and Taste Luncheon | 20 |
| 2025-06-10 | 15:00–17:00 | Artful Athletics: Paint & Play Extravaganza | 15 |
| 2025-06-10 | 19:00–21:00 | AgentsVille Twilight Writing Escape | 15 |
| 2025-06-11 | 09:00–10:30 | Morning Groove Dance Party | 15 |
| 2025-06-11 | 12:00–13:30 | Tech Lunch & Learn: AI Frontiers | 20 |
| 2025-06-11 | 15:00–17:30 | AgentsVille Art & Music Fusion Fest | 18 |
| 2025-06-11 | 18:30–20:30 | Palette & Palate: Art Meets Cooking Experience | 25 |
| 2025-06-12 | 08:00–10:00 | AgentsVille Nature & Green Thumb Adventure | 15 |
| 2025-06-12 | 12:00–13:30 | Soundtrack Picnic: Lunchtime Movies & Melodies | 15 |
| 2025-06-12 | 14:00–16:30 | Trail Tales: Writing & Hiking Adventure | 20 |
| 2025-06-12 | 19:00–21:30 | Tech & Film Fusion Night | 15 |

June 12 has thunderstorms. The planner needs to read the activity descriptions and choose indoor activities or activities with an explicit indoor backup. For example, the writing-and-hiking activity on that day is outdoors, while the cinema event says it moves indoors if it rains.

## Checks run

All 47 tests passed. The notebook-kernel test runs cells 1–12 with network requests blocked. Other tests cover required fields, invalid dates, negative and noninteger budgets, invalid traveler details, unsupported interests, unavailable data, and inclusive date lookups for one-day, three-day, and six-day trips.

The schema and date lookups now satisfy rubric criterion R5. The planner and evaluation prompts are still unfinished; there is no generated itinerary yet.

Next: complete the initial planner prompt, include the TravelPlan schema and retrieved data, and inspect the first generated itinerary.
