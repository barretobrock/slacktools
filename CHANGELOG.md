# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

_Note: 'Unreleased' section below is used for untagged changes that will be issued with the next version bump_

### [Unreleased] - 2022-00-00
#### Added
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
__BEGIN-CHANGELOG__
 
### [1.7.5] - 2022-07-31
#### Fixed
 - Slash commands were failing to parse the new command structure

### [1.7.4] - 2022-07-31
#### Added
 - Test for command builder
#### Fixed
 - Improved mocking of pin/message event structure
 - Command builder missing references to new naming patterns
 - Bad attr call to message event data

### [1.7.3] - 2022-07-31
#### Added
 - Documented example api responses to (later) better test class construction more thoroughly
#### Changed
 - Broke out api into web, events and slash - potentially more to come
#### Fixed
 - Classes now parse nested dictionary info in 1 pass instead of the more broken methodology of patching in nested items later

### [1.7.2] - 2022-07-30
#### Added
 - EmojiEvent Factory
 - Bundled message event types

### [1.7.1] - 2022-07-29
#### Added
 - `make_section_with_image` method

### [1.7.0] - 2022-06-10
#### Added
 - Events API types
 - add `pre-commit`
#### Changed
 - [GH-3](../../issues/3) - Block Kit refactored and expanded to include all elements used in sections / messages, with type hinting
#### Fixed
 - [GH-2](../../issues/2) - Exceptions still posting in Slack

### [1.6.2] - 2022-05-18
#### Fixed
 - Events structure in Slack changes because it's sneaky. This change makes events parsing a tad more flexible.

### [1.6.1] - 2022-05-14
#### Added
 - in-thread messaging support

### [1.6.0] - 2022-04-23
#### Added
 - Python 3.10 support

### [1.5.9] - 2022-04-23
#### Added
 - mock_commands to help with testing

### [1.5.8] - 2022-04-15
#### Added
 - Search commands
#### Fixed
 - Help block now properly builds

### [1.5.7] - 2022-04-15
#### Changed
 - Command help section builder broken out so it can be shared in command search methods

### [1.5.6] - 2022-04-10
#### Changed
 - structure of command block now uses tabs to better organise groups
#### Fixed
 - Command flags weren't being called properly in the command builder
 - Malformed list in letter organizer

### [1.5.5] - 2022-04-10
#### Fixed
 - command read-in was failing due to improper YAML structure

### [1.5.4] - 2022-04-09
#### Added
 - command builder standalone function
 - PyYAML to reqs
#### Changed
 - commands now stored in YAML to better organize base
 - command dict is now a list with tags!
 - command list no longer required upon instantiation

### [1.5.3] - 2022-04-09
#### Added
 - database engine base class & tests for the bots
 - Inital `Slass`-based classes for making Slack responses more helpful in OOP
#### Changed
 - Broke out slack procedures into more organized methods
#### Removed
 - Baked-in google sheet methods from slack tools, as it's a lot to spin up.

### [1.5.2] - 2022-04-08
#### Added
 - real tests finally!
 - more emojis in the character mapper
 - `loguru` for logging support
#### Removed
 - `easylogger` as logger
#### Fixed
 - missing completion bracket in slack link builder

### [1.5.1] - 2022-04-08
#### Added
 - `tox`
#### Changed
 - Improved how PPM handles variable scope
 - Imported the only method used in kavalkilu to reduce dependency load

### [1.5.0] - 2022-04-08
#### Added
 - CHANGELOG
 - pyproject.toml
 - poetry.lock
#### Changed
 - Completed switch to poetry
 - Shifted to new PPM routine for package management
#### Deprecated
 - Versioneer
#### Removed
 - Lots of PPM-dependent files



__END-CHANGELOG__
