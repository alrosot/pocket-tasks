## MODIFIED Requirements

### Requirement: home-screen-placeholders

Each section of the home screen MUST display a placeholder for a child's dashboard, including the child's icon.

#### Scenario: Home Screen Display

- Given the home screen is displayed.
- Then each of the two sections MUST contain a UI element representing a child's dashboard with an associated icon.

## ADDED Requirements

### Requirement: home-screen-kid-icons

Each child's dashboard section MUST display the child's icon.

#### Scenario: Icon Display

- Given the home screen is displayed.
- And each child has an associated icon file in `/assets/images`.
- When the home screen is rendered.
- Then each child's dashboard section MUST display the corresponding icon.