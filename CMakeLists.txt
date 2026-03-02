PROJECT (symai)

CMAKE_MINIMUM_REQUIRED (VERSION 3.12)

LIST(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/etc/cmake)
FIND_PACKAGE(Go REQUIRED)

SET(PROJECT_BUILD_DIR "build")
SET(SYMAI_VER_MAJOR 1)
SET(SYMAI_VER_MINOR 1)
SET(SYMAI_VER_PATCH 0)

SET (PROJECT_SOURCE_DIR, ${CMAKE_SOURCE_DIR})
SET (BASE_PATH ${PROJECT_SOURCE_DIR})
SET (PROJECT_BUILD_DIR ${BASE_PATH}/build)
SET (LOGDIR ${BASE_PATH}/logdir)
SET (TMP_DIR ${BASE_PATH}/temp)
SET (RESOURCES ${BASE_PATH}/resources)
SET (PROPERTIES ${BASE_PATH}/properties)

SET (FRONTEND_BINARY_NAME "frontend")
SET (SYMAICORE_BINARY_NAME "symaicore")

MESSAGE (STATUS "Project ${CMAKE_PROJECT_NAME} build ")

FIND_PACKAGE(Python COMPONENTS Interpreter Development)

ADD_CUSTOM_TARGET(make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET make-work-dirs
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server"
    COMMAND mkdir -p ${LOGDIR}
    COMMAND mkdir -p ${TMP_DIR}
    COMMAND mkdir -p ${RESOURCES}
    COMMAND mkdir -p ${PROPERTIES}
    DEPENDS "${PROJECT_SOURCE_DIR}/src/python/antlr4/BehaviorsGrammar.g4"
)

ADD_CUSTOM_TARGET(antlr4-generate-behaviors-golang)
ADD_CUSTOM_COMMAND(TARGET antlr4-generate-behaviors-golang
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/go/server"
    COMMAND java -jar ${PROJECT_SOURCE_DIR}/bin/antlr-4.13.1-complete.jar ${PROJECT_SOURCE_DIR}/src/antlr4/BehaviorsGrammar.g4 -Dlanguage=Go -encoding UTF8 -package BehaviorsGrammar -o BehaviorsGrammar -visitor -no-listener
    DEPENDS "${PROJECT_SOURCE_DIR}/src/antlr4/BehaviorsGrammar.g4"
)

ADD_CUSTOM_TARGET(symai-mod-prepare)
ADD_CUSTOM_COMMAND(TARGET symai-mod-prepare
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/go"
     COMMAND rm -f go.mod
     COMMAND rm -f go.sum
     COMMAND ${GO_EXECUTABLE} mod init src
     COMMAND ${GO_EXECUTABLE} mod tidy     
)

ADD_CUSTOM_TARGET(symai-test-golang)
ADD_CUSTOM_COMMAND(TARGET symai-test-golang DEPENDS antlr4-generate-behaviors-golang symai-mod-prepare
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/go/server"
   COMMAND go test -benchmem -cover ./...
)

ADD_CUSTOM_TARGET(antlr4-generate-behaviors DEPENDS antlr4-generate-behaviors-golang)
ADD_CUSTOM_COMMAND(TARGET antlr4-generate-behaviors
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server"
    COMMAND java -jar ${PROJECT_SOURCE_DIR}/bin/antlr-4.13.1-complete.jar ${PROJECT_SOURCE_DIR}/src/antlr4/BehaviorsGrammar.g4 -Dlanguage=Python3 -encoding UTF8 -package BehaviorsGrammar -o BehaviorsGrammar -visitor
    DEPENDS "${PROJECT_SOURCE_DIR}/src/antlr4/BehaviorsGrammar.g4"
)

ADD_CUSTOM_TARGET(symai-symaicore-golang DEPENDS antlr4-generate-behaviors-golang symai-mod-prepare)
ADD_CUSTOM_COMMAND(TARGET symai-symaicore-golang
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/go/server"
   COMMAND go build -tags DEBUG -ldflags "-X main.build=DEBUG -X main.major=1 -X main.minor=1 -X main.patch=0 -X main.buildDate=$ENV{CURRENT_UTC_DATE}" -o ${PROJECT_BUILD_DIR}/debug/${SYMAICORE_BINARY_NAME} symaicore/symaicore.go
   COMMAND go build -tags RELEASE -ldflags "-X main.build=RELEASE -X main.major=1 -X main.minor=1 -X main.patch=0 -X main.buildDate=$ENV{CURRENT_UTC_DATE}" -o ${PROJECT_BUILD_DIR}/release/${SYMAICORE_BINARY_NAME} symaicore/symaicore.go
)

ADD_CUSTOM_TARGET(symai-frontend-golang DEPENDS symai-mod-prepare)
ADD_CUSTOM_COMMAND(TARGET symai-frontend-golang
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/go/server"
   COMMAND go build -tags DEBUG -ldflags "-X main.build=DEBUG -X main.major=1 -X main.minor=1 -X main.patch=0 -X main.buildDate=$ENV{CURRENT_UTC_DATE}" -o ${PROJECT_BUILD_DIR}/debug/${FRONTEND_BINARY_NAME} frontend/frontend.go
   COMMAND go build -tags RELEASE -ldflags "-X main.build=RELEASE -X main.major=1 -X main.minor=1 -X main.patch=0 -X main.buildDate=$ENV{CURRENT_UTC_DATE}" -o ${PROJECT_BUILD_DIR}/release/${FRONTEND_BINARY_NAME} frontend/frontend.go
)

ADD_CUSTOM_TARGET(symai-test DEPENDS antlr4-generate-behaviors)
ADD_CUSTOM_COMMAND(TARGET symai-test
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server"
    COMMAND ${Python_EXECUTABLE} ${PROJECT_SOURCE_DIR}/src/python/server/test_symai.py
    DEPENDS antlr4-generate-behaviors
)

ADD_CUSTOM_TARGET(symai-expression-docker-build DEPENDS antlr4-generate-behaviors make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET symai-expression-docker-build
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose build expression
)

ADD_CUSTOM_TARGET(symai-core-docker-build DEPENDS make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET symai-core-docker-build
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose build core_go
)

ADD_CUSTOM_TARGET(symai-client DEPENDS make-work-dirs)
ADD_CUSTOM_COMMAND(TARGET symai-client
                   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server/resources/client"
    COMMAND ng build --configuration=production
)

ADD_CUSTOM_TARGET(symai-frontend-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-frontend-docker-build
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose build frontend_go
)

ADD_CUSTOM_TARGET(symai-docker-build DEPENDS symai-expression-docker-build symai-core-docker-build symai-frontend-docker-build)

ADD_CUSTOM_TARGET(symai-docker DEPENDS antlr4-generate-behaviors)
ADD_CUSTOM_COMMAND(TARGET symai-docker
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose build
)

ADD_CUSTOM_TARGET(symai-expression-docker-run DEPENDS symai-expression-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-expression-docker-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up expression
)

ADD_CUSTOM_TARGET(symai-core-docker-run DEPENDS symai-core-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-core-docker-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up core_go
)

ADD_CUSTOM_TARGET(symai-frontend-docker-run DEPENDS symai-frontend-docker-build)
ADD_CUSTOM_COMMAND(TARGET symai-frontend-docker-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up frontend_go
)

ADD_CUSTOM_TARGET(symai-run DEPENDS symai-docker)
ADD_CUSTOM_COMMAND(TARGET symai-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/docker"
    COMMAND sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up
)

ADD_CUSTOM_TARGET(symai ALL DEPENDS symai-docker
)
ADD_CUSTOM_TARGET(cleanall
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/build/*"
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/src/python/server/BehaviorsGrammar"
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/src/python/server/__pycache__"
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/src/go/server/BehaviorsGrammar"
)

