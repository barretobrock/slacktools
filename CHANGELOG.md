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
 
### [2.0.9] - 2024-01-14
#### Fixed
 - Removed invalid `block_id` from button element (this is only valid for blocks, not individual elements)
 
### [2.0.8] - 2024-01-14
#### Added
 - Option to provide random response on command mismatch
#### Changed
 - Command parsing is now handled through dedicated objects 
 - Help and help search redesigned to use blocks
 - Minor class variable refactoring to better conform to duck typing
 
### [2.0.7] - 2023-12-25
#### Added
 - [GH-13](../../issues/13) - Add tiny text generation support
 - Add initial action form support
#### Fixed
 - [GH-14](../../issues/14) - Undo ephemeral default on slash commands
 - [GH-15](../../issues/15) - Bot mention regex was greedy
 - Bypass warning on `text` param being empty with sending blocks notis
 
### [2.0.6] - 2023-12-23
#### Added
 - Allow `is_in_bot_timeout` check on incoming messages, commands and actions
 - Channel event classes
 
### [2.0.5] - 2023-12-22
#### Added
 - `BaseApiObject`s now also have `asdict` to help with conversion where needed (e.g., blocks replacement)
#### Fixed
 - [GH-12](../../issues/12) - Slash commands with args should now replace filler args
 
### [2.0.4] - 2023-12-21
#### Added
 - Tests for handle_commands for both `Message` and `Slash` objects
 - Admin-only command support
#### Changed
 - When slash commands are used, try to respond in ephemeral, noting that we can't use slash in threads.
#### Fixed
 - `ButtonTextElement`s now render with markdown instead of plaintext
 
### [2.0.3] - 2023-12-19
#### Changed
 - Revert to props over namespace
 - Add ephemeral main channel messaging method
 - Placeholder params are now fully optional
 
### [2.0.2] - 2023-12-18
#### Added
 - `BlocksType` to help with type hints
 - `PlainTextHeaderBlock`
#### Changed
 - Slack methods that use blocks now scan blocks for convertible elements before sending
#### Fixed
 - Capitalization on a class name
 
### [2.0.1] - 2023-12-16
#### Changed
 - Migrated to `slack-sdk`
 - Block kit classes now behave more like classes than dicts
 - Update `pre-commit` plugins
#### Deprecated
 - `BlockKitBuilder`
 
### [2.0.0] - 2023-08-11
#### Added
 - Python 3.11 support

### [1.7.6] - 2022-07-31
#### Added
 - Better mocking methods for slack responses
 - More tests for events
#### Fixed
 - Erroneous call to Union instantiation instead of typed dict

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
