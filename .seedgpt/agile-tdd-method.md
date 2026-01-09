On seedgpt the planting is done once. 
from that point we will do this in a loop:
1. status recap  - evaluate new client communication, where were at, update docs accordingly. check if we need to update the roadmap and PRD according to recent work. check the git status and commit the changes if needed. check current roadmap and PRD and client communication and current state of the project in the filesystem and update the sprint plan accordingly.
2. planning - plan the next sprint. We multiple the work effort by 2 and seperate to 2 different developers - test and dev. The tester starts first and provides a black-box testing code that tests and verifies the PRD as a blackbox and using the app's officials APIs (he can write himself utilities and simulators and mocks and unittests for his verification code), the dev writes his code and delivers the require feature (he also creates his own unittests). this is done on feature-name/dev and feature-name/test branches (e.g)
3. a. Implementation - each worker (dev/test) fully implmenets his tasks and pass his local tests.
3. b. update plans
4. integration - both test and dev are merge into feature-name branch and tests are executed, and dev/test code is debugged until all tests pass.
5. a. Merge - feature-name branch is merged to main branch, and all tests cycle runs again and code/tests are debugged and fixed until its all green.
5. b. update plans
6. a. Deploy, test post deployment 
6. b. update plans
7. meet with client and present results, analyse them etc. 
8. gather new inputs and record them. 
9. update docs and roadmap and PRD and client communication and current state of the project in the filesystem and update the sprint plan accordingly.
