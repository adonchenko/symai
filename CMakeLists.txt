PROJECT (symai)

CMAKE_MINIMUM_REQUIRED (VERSION 3.12)

SET(PROJECT_BUILD_DIR "build")
SET(TEST_VER_MAJOR 1)
SET(TEST_VER_MINOR 1)

SET (PROJECT_SOURCE_DIR, ${CMAKE_SOURCE_DIR})
SET (BASE_PATH ${PROJECT_SOURCE_DIR})
SET (LOGDIR ${BASE_PATH}/logdir)
SET (TMP_DIR ${BASE_PATH}/temp)
SET (RESOURCES ${BASE_PATH}/resources)
SET (PROPERTIES ${BASE_PATH}/properties)

MESSAGE (STATUS "Project ${CMAKE_PROJECT_NAME} build ")

find_package(Python COMPONENTS Interpreter Development)

ADD_CUSTOM_TARGET(make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET make-work-dirs
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server"
    COMMAND mkdir -p ${LOGDIR}
    COMMAND mkdir -p ${TMP_DIR}
    COMMAND mkdir -p ${RESOURCES}
    COMMAND mkdir -p ${PROPERTIES}
    DEPENDS "${PROJECT_SOURCE_DIR}/src/python/antlr4/ExpressionGrammar.g4"
)

ADD_CUSTOM_TARGET(antlr4-generate-expression)
ADD_CUSTOM_COMMAND(TARGET antlr4-generate-expression
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server"
    COMMAND java -jar ${PROJECT_SOURCE_DIR}/src/python/bin/antlr-4.13.1-complete.jar ${PROJECT_SOURCE_DIR}/src/python/server/antlr4/ExpressionGrammar.g4 -Dlanguage=Python3 -encoding UTF8 -package ExpressionGrammar -o ExpressionGrammar -visitor
    DEPENDS "${PROJECT_SOURCE_DIR}/src/python/antlr4/ExpressionGrammar.g4"
)

ADD_CUSTOM_TARGET(symai-test)
ADD_CUSTOM_COMMAND(TARGET symai-test
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server"
    COMMAND ${Python_EXECUTABLE} ${PROJECT_SOURCE_DIR}/src/python/server/test_symai.py
    DEPENDS antlr4-generate-expression
)

ADD_CUSTOM_TARGET(symai-expression-docker-build DEPENDS antlr4-generate-expression make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET symai-expression-docker-build
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose build expression
)

ADD_CUSTOM_TARGET(symai-core-docker-build DEPENDS antlr4-generate-expression make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET symai-core-docker-build
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose build core
)

ADD_CUSTOM_TARGET(symai-client DEPENDS make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET symai-client
                   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/resources/client"
    COMMAND ng build --configuration=production
)


ADD_CUSTOM_TARGET(symai-frontend-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-frontend-docker-build
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up frontend
)

ADD_CUSTOM_TARGET(symai-docker-build DEPENDS symai-expression-docker-build symai-core-docker-build symai-frontend-docker-build)

ADD_CUSTOM_TARGET(symai-docker DEPENDS antlr4-generate-expression)
ADD_CUSTOM_COMMAND(TARGET symai-docker
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/etc/tools"
    COMMAND sudo ./build-docker.sh
)

ADD_CUSTOM_TARGET(symai-expression-docker-run DEPENDS symai-expression-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-expression-docker-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up expression
)

ADD_CUSTOM_TARGET(symai-core-docker-run DEPENDS symai-core-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-core-docker-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up core
)

ADD_CUSTOM_TARGET(symai-frontend-docker-run DEPENDS symai-frontend-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-frontend-docker-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up frontend
)

ADD_CUSTOM_TARGET(symai-run DEPENDS symai-docker)
ADD_CUSTOM_COMMAND(TARGET symai-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up
)

ADD_CUSTOM_TARGET(symai ALL DEPENDS symai-docker
)
ADD_CUSTOM_TARGET(cleanall
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/build/*"
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/src/python/server/ExpressionGrammar"
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/src/python/server/__pycache__"
)

