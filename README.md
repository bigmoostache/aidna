Mind <-> Body <-> Environment

## Basic system

- Body observes Env through Senses
- Body has a State
- State evolves based on State and Environment
- Body provides Mind Actions that my update State
- Environment provides a list of Games
- Games provide Food
- Food can be consumed to gain Energy
- Everything costs Energy: Body Observations, Mind - Body interations, Actions
- Environment sacrifices randomly Individuals based on their State (Age, Food, Energy, etc.)
- Sacrifices causes Mutations

## Environment

- Provides games
- Games are validated based solely on a Body/Bodies's State

## Idea

- Prove that emergence can occur
- Use that emergence to reach AGI

## Technical implementation

- Monorepo
- Multi branches
- Main branch determines environment, bodies, orchestration, etc
- Individual-XXX branches define Minds
- Individuals may go through a build phase, then are deployed using a set of docker images.
- Claude code + local branch defined logic (which may mutate too) defines mutations