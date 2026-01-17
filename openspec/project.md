# Project Context

## Purpose
Enable kids to track their tasks in a fun way. It's called pocket-tasks.
We are building software that will run in a RaspberryPi computer with a touch screen embedded. The RaspberryPi device will be dedicated to this single application. The software will be able to support a family, i.e. more than one kid.
Through simple and engaging interactions, the kids will be able to check what weekly tasks are pending and how many of them they completed already. For each completed task they'll receive some money

## Tech Stack
- RaspberryPi as platform
- Waveshare 2.13" Touch e-Paper HAT for the display.
- PIL/Pillow Library
- Python
- plain file system storage to save each kid's weekly progress
- Amazon SES

## Project Conventions

### Testing Strategy
- unit tests for all the changes
- a Makefile command spins up `luma.emulator` to perform manual tests without having to have the RaspberryPi and screen connected

### Deployment Strategy
We'll have a cronjob running on the raspberryPi that every night, at 2am, does the following:
- Stops pocket-tasks
- Gets the latest source code from github
- Starts pocket-tasks

### Visual Identity
Even though our selected display only supports two colours (black and white) and 250×122 resolution, the interface should be joyful. Consider having:
- round buttons
- pixel art
- minimal transition elements due to the low refresh speed

### Git Workflow
- PRs can only be merged once all the unit tests are passing
