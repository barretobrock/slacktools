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