project (UQTk)

SET(copy_FILES
  quadpnts.txt
  quadwghts.txt
  )
INSTALL(FILES ${copy_FILES} DESTINATION cpp/tests/QuadLUTest/)

add_executable (QuadLUTest main.cpp)

target_link_libraries (QuadLUTest uqtk  )

target_link_libraries (QuadLUTest depdsfmt )
target_link_libraries (QuadLUTest sundials_core)
target_link_libraries (QuadLUTest sundials_cvode)
target_link_libraries (QuadLUTest sundials_nvecserial)
target_link_libraries (QuadLUTest sundials_sunlinsoldense)
target_link_libraries (QuadLUTest sundials_sunmatrixdense)
target_link_libraries (QuadLUTest depslatec)
target_link_libraries (QuadLUTest deplbfgs )
target_link_libraries (QuadLUTest depfigtree )
target_link_libraries (QuadLUTest depann   )

# Link fortran libraries
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  # using GCC
  target_link_libraries (QuadLUTest gfortran expat stdc++)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
  # using Intel
  if ("${IntelLibPath}" STREQUAL "")
    target_link_libraries (QuadLUTest ifcore)
  else()
    target_link_libraries (QuadLUTest ${IntelLibPath}/libifcore.a)
  endif()
elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  # using Clang
  if ("${ClangLibPath}" STREQUAL "")
    target_link_libraries (QuadLUTest gfortran stdc++)
  else()
    target_link_libraries (QuadLUTest ${ClangLibPath}/libgfortran.dylib  ${ClangLibPath}/libstdc++.dylib)
  endif()
endif()

target_link_libraries (QuadLUTest m lapack ${LAPACK_LIBRARIES})
target_link_libraries (QuadLUTest m blas ${BLAS_LIBRARIES})

include_directories(../../lib/pce    )
include_directories(../../lib/array  )
include_directories(../../lib/include)
include_directories(../../lib/quad   )
include_directories(../../lib/tools  )
include_directories(../../lib/mcmc  )

include_directories(../../../dep/dsfmt)
include_directories(../../../dep/slatec)
include_directories(../../../dep/lbfgs)

INSTALL(TARGETS QuadLUTest DESTINATION bin/tests/)

add_test(QuadLUTest QuadLUTest)
