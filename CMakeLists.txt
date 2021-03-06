cmake_minimum_required(VERSION 2.6)

set(PACKAGE_NAME morse)
set(PACKAGE_VERSION 0.4.99)

option(BUILD_CORE_SUPPORT "Build and install morse core" ON)
option(BUILD_DOC_SUPPORT "Build and install morse documentation (Requiere Sphinx)" ON)

option(BUILD_POCOLIBS_SUPPORT "Build pocolibs framework support" OFF)
option(BUILD_YARP2_SUPPORT "Build yarp framework support" OFF)
option(BUILD_ROS_SUPPORT "Build ROS middleware support" OFF)
option(BUILD_MOOS_SUPPORT "Build MOOS middleware support" OFF)
option(BUILD_HLA_SUPPORT "Build HLA middleware support. Also used for distributed HLA simulation." OFF)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/config/)
find_package(PkgConfig REQUIRED)

find_package(Python32Interp REQUIRED)
find_package(Python32Libs REQUIRED)

EXECUTE_PROCESS(COMMAND
				${PYTHON3_EXECUTABLE} -c "import distutils.sysconfig, sys; sys.stdout.write(distutils.sysconfig.get_python_lib(0,0,\"\"))"
					OUTPUT_VARIABLE PYTHON_INSTALL
					ERROR_VARIABLE PYTHON_STDERR
					RESULT_VARIABLE PYTHON_ERR
				)

SET(PYTHON_INSTDIR ${CMAKE_INSTALL_PREFIX}/${PYTHON_INSTALL}) 
MESSAGE(STATUS "will install python files in ${PYTHON_INSTDIR}")

if (NOT PYTHON3INTERP_FOUND)
	MESSAGE(FATAL_ERROR "Can't find python 3.2 on your system")
endif(NOT PYTHON3INTERP_FOUND)
if (BUILD_YARP2_SUPPORT)
	EXECUTE_PROCESS(COMMAND 
					${PYTHON3_EXECUTABLE} -c "import yarp;"
					RESULT_VARIABLE YARP_PY_ERR
				   )
	if (YARP_PY_ERR)
		MESSAGE(FATAL_ERROR "BUILD_YARP_SUPPORT is required, but '${PYTHON3_EXECUTABLE}' can't find yarp python binding")
	endif (YARP_PY_ERR)
endif(BUILD_YARP2_SUPPORT)


# check to make sure pymoos is installed
if (BUILD_MOOS_SUPPORT)
	EXECUTE_PROCESS(COMMAND 
					${PYTHON3_EXECUTABLE} -c "import pymoos.MOOSCommClient;"
					RESULT_VARIABLE MOOS_PY_ERR
				   )
	if (MOOS_PY_ERR)
		#message(${MOOS_PY_ERR})
		#MESSAGE(FATAL_ERROR "BUILD_MOOS_SUPPORT is required, but '${PYTHON3_EXECUTABLE}' can't find MOOS python binding")
	endif (MOOS_PY_ERR)
endif(BUILD_MOOS_SUPPORT)


IF (BUILD_POCOLIBS_SUPPORT)
	pkg_check_modules(POCOLIBS REQUIRED pocolibs)
	find_package(SWIG REQUIRED)
endif(BUILD_POCOLIBS_SUPPORT)

if (BUILD_HLA_SUPPORT)
	EXECUTE_PROCESS(COMMAND 
					${PYTHON3_EXECUTABLE} -c "import hla;"
					RESULT_VARIABLE HLA_PY_ERR
				   )
	if (HLA_PY_ERR)
		MESSAGE(FATAL_ERROR "BUILD_HLA_SUPPORT is required, but '${PYTHON3_EXECUTABLE}' can't find 'hla' python binding")
	endif (HLA_PY_ERR)
endif(BUILD_HLA_SUPPORT)

ADD_SUBDIRECTORY(src)
enable_testing()
ADD_SUBDIRECTORY(testing)

IF(BUILD_CORE_SUPPORT)
INSTALL (DIRECTORY data examples
	     DESTINATION ${CMAKE_INSTALL_PREFIX}/share
         REGEX .*blend.$ EXCLUDE
         REGEX .*py.$ EXCLUDE
		 REGEX .*clients.* EXCLUDE
		)

CONFIGURE_FILE(
	${CMAKE_CURRENT_SOURCE_DIR}/bin/morse.in
	${CMAKE_CURRENT_BINARY_DIR}/bin/morse
	)
CONFIGURE_FILE(
	${CMAKE_CURRENT_SOURCE_DIR}/bin/morseexec.in
	${CMAKE_CURRENT_BINARY_DIR}/bin/morseexec
	)
INSTALL(PROGRAMS
		${CMAKE_CURRENT_BINARY_DIR}/bin/morse
		${CMAKE_CURRENT_BINARY_DIR}/bin/morseexec
		DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
	    )
ENDIF()


IF (BUILD_DOC_SUPPORT)
### Doc target ###
CONFIGURE_FILE(
	${CMAKE_CURRENT_SOURCE_DIR}/doc/conf.py.in
	${CMAKE_CURRENT_BINARY_DIR}/doc/conf.py
	)

FIND_PROGRAM(SPHINX_BUILD NAMES sphinx-build)
IF (NOT SPHINX_BUILD)
	MESSAGE(STATUS "Can't find sphinx-build : will not build the documentation")
ELSE()
	SET (SPHINX_OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/doc/html)
	SET (SPHINX_LATEX_OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/doc/tex)
	ADD_CUSTOM_COMMAND(
		OUTPUT ${SPHINX_OUTPUT}
		COMMAND ${SPHINX_BUILD} -b html
								-c ${CMAKE_CURRENT_BINARY_DIR}/doc
								   ${CMAKE_CURRENT_SOURCE_DIR}/doc/morse
								   ${SPHINX_OUTPUT}
	)

	ADD_CUSTOM_TARGET(doc ALL DEPENDS ${SPHINX_OUTPUT})

	INSTALL(DIRECTORY ${SPHINX_OUTPUT}
			DESTINATION ${CMAKE_INSTALL_PREFIX}/share/doc/morse
			REGEX .doctrees.* EXCLUDE
			REGEX _sources.* EXCLUDE
			REGEX .*.inv EXCLUDE
			REGEX .buildinfo EXCLUDE
			)

	ADD_CUSTOM_TARGET(
		force_doc
		COMMAND ${SPHINX_BUILD} -b html 
								-c ${CMAKE_CURRENT_BINARY_DIR}/doc/
								${CMAKE_CURRENT_SOURCE_DIR}/doc/morse
								${SPHINX_OUTPUT}
	)

	ADD_CUSTOM_TARGET(
		latex_doc
		COMMAND ${SPHINX_BUILD} -b latex
								-c ${CMAKE_CURRENT_BINARY_DIR}/doc/
								${CMAKE_CURRENT_SOURCE_DIR}/doc/morse
								${SPHINX_LATEX_OUTPUT}
	)
ENDIF()
ENDIF()

### CPack ###
EXECUTE_PROCESS(COMMAND
				which dpkg
					OUTPUT_VARIABLE SYSTEST_DPKG)
EXECUTE_PROCESS(COMMAND
				which rpm
					OUTPUT_VARIABLE SYSTEST_RPM)
IF (SYSTEST_DPKG)
	SET(CPACK_GENERATOR "DEB")
ELSEIF (SYSTEST_RPM)
	SET(CPACK_GENERATOR "RPM")
ELSE ()
	SET(CPACK_GENERATOR "TGZ")
ENDIF()
# TODO find a better way to check debian or redhat ?

SET(CPACK_PACKAGE_CONTACT "morse-users <morse-users@laas.fr>")
SET(CPACK_PACKAGE_DESCRIPTION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/README")
SET(CPACK_PACKAGE_DESCRIPTION_SUMMARY "MORSE the Open Robots Simulator")
SET(CPACK_PACKAGE_NAME "openrobots-morse")
SET(CPACK_PACKAGE_VENDOR "CNRS/LAAS")
SET(CPACK_PACKAGE_VERSION ${PACKAGE_VERSION})
SET(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
SET(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/README")

SET(CPACK_DEBIAN_PACKAGE_DEPENDS "python3-dev")
SET(CPACK_DEBIAN_PACKAGE_HOMEPAGE "http://morse.openrobots.org")

INCLUDE(CPack)

### Uninstall ###
configure_file("${CMAKE_HOME_DIRECTORY}/config/cmake_uninstall.cmake.in" "cmake_uninstall.cmake" IMMEDIATE @ONLY)
add_custom_target(uninstall "${CMAKE_COMMAND}" -P "cmake_uninstall.cmake")

