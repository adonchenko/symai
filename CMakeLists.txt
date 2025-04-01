PROJECT (symai)

CMAKE_MINIMUM_REQUIRED (VERSION 3.12)

SET(PROJECT_BUILD_DIR "build")
SET(TEST_VER_MAJOR 1)
SET(TEST_VER_MINOR 1)

ADD_CUSTOM_TARGET(antlr4-generate-expression)
ADD_CUSTOM_COMMAND(TARGET antlr4-generate-expression
          WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/server"
    COMMAND java -jar ${PROJECT_SOURCE_DIR}/src/python/bin/antlr-4.13.1-complete.jar ${PROJECT_SOURCE_DIR}/src/python/server/antlr4/ExpressionGrammar.g4 -Dlanguage=Python3 -encoding UTF8 -package ExpressionGrammar -o ExpressionGrammar -visitor
    DEPENDS "${PROJECT_SOURCE_DIR}/src/python/antlr4/ExpressionGrammar.g4"
)

ADD_CUSTOM_TARGET(symai-expression-docker DEPENDS antlr4-generate-expression)
ADD_CUSTOM_COMMAND(TARGET symai-expression-docker
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/etc/tools"
    COMMAND sudo ./build-docker.sh
)

ADD_CUSTOM_TARGET(symai-expression-docker-run DEPENDS symai-expression-docker)
ADD_CUSTOM_COMMAND(TARGET symai-expression-docker-run
		   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src/python/etc/tools"
    COMMAND sudo ./run-docker.sh
)

ADD_CUSTOM_TARGET(symai ALL DEPENDS symai-expression-docker
)
ADD_CUSTOM_TARGET(cleanall
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/build/*"
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/src/python/server/ExpressionGrammar"
  COMMAND rm -rf "${PROJECT_SOURCE_DIR}/src/python/server/__pycache__"
)

