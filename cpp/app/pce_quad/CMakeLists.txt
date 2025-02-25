project (UQTk)

link_directories(${CMAKE_SUNDIALS_DIR}/lib)

add_executable (pce_quad pce_quad.cpp)

target_link_libraries (pce_quad uqtkpce  )
target_link_libraries (pce_quad uqtkquad )
target_link_libraries (pce_quad uqtktools)
target_link_libraries (pce_quad uqtkarray)

target_link_libraries (pce_quad depdsfmt )
target_link_libraries (pce_quad sundials_core)
target_link_libraries (pce_quad sundials_cvode)
target_link_libraries (pce_quad sundials_nvecserial)
target_link_libraries (pce_quad sundials_sunlinsoldense)
target_link_libraries (pce_quad sundials_sunmatrixdense)
target_link_libraries (pce_quad depslatec)
target_link_libraries (pce_quad depfigtree )
target_link_libraries (pce_quad depann   )

# Link fortran libraries
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  # using GCC
  if ("${GnuLibPath}" STREQUAL "")
    target_link_libraries (pce_quad gfortran stdc++)
  else()
    target_link_libraries (pce_quad ${GnuLibPath}/libgfortran.a ${GnuLibPath}/libquadmath.a stdc++)
  endif()
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
  # using Intel
  if ("${IntelLibPath}" STREQUAL "")
    target_link_libraries (pce_quad ifcore)
  else()
    target_link_libraries (pce_quad ${IntelLibPath}/libifcore.a)
  endif()
elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  # using Clang
  if ("${ClangLibPath}" STREQUAL "")
    target_link_libraries (pce_quad gfortran stdc++)
  else()
    target_link_libraries (pce_quad ${ClangLibPath}/libgfortran.dylib ${ClangLibPath}/libquadmath.dylib ${ClangLibPath}/libstdc++.dylib)
  endif()
endif()

target_link_libraries (pce_quad m lapack ${LAPACK_LIBRARIES})
target_link_libraries (pce_quad m blas ${BLAS_LIBRARIES})

include_directories(../../lib/pce    )
include_directories(../../lib/array  )
include_directories(../../lib/include)
include_directories(../../lib/quad   )
include_directories(../../lib/tools  )

include_directories(../../../dep/dsfmt)
include_directories(../../../dep/figtree)
include_directories (${CMAKE_SUNDIALS_DIR}/include)
if( BUILD_SUNDIALS)
  include_directories (../../../dep/sundials/include )
  include_directories ("${PROJECT_BINARY_DIR}/../../../dep/sundials/include")
endif()
INSTALL(TARGETS pce_quad DESTINATION bin)
