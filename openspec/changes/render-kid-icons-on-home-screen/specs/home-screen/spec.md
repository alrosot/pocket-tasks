## MODIFIED Requirements

### Requirement: home-screen-kid-sections

Each section of the home screen MUST display a dashboard for each registered child.

#### Scenario: Home Screen Display

- Given the home screen is displayed.
- Then each of the two sections MUST contain a UI element representing a child's dashboard.

## ADDED Requirements

### Requirement: home-screen-kid-icons

Each child's dashboard section MUST display the child's icon.

#### Scenario: Icon Display

- Given the home screen is displayed.
- And each child has an associated icon file in `/assets/images`.
- When the home screen is rendered.
- Then each child's dashboard section MUST display the corresponding icon.
