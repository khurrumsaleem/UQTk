project (UQTk)

add_executable (PCEImplTest main.cpp)

target_link_libraries (PCEImplTest uqtk )

target_link_libraries (PCEImplTest depdsfmt )
target_link_libraries (PCEImplTest sundials_core)
target_link_libraries (PCEImplTest sundials_cvode)
target_link_libraries (PCEImplTest sundials_nvecserial)
target_link_libraries (PCEImplTest sundials_sunlinsoldense)
target_link_libraries (PCEImplTest sundials_sunmatrixdense)
target_link_libraries (PCEImplTest depslatec)
target_link_libraries (PCEImplTest deplbfgs  )
target_link_libraries (PCEImplTest depfigtree  )
target_link_libraries (PCEImplTest depann  )


# Link fortran libraries
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  # using GCC
  target_link_libraries (PCEImplTest gfortran expat stdc++)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
  # using Intel
  if ("${IntelLibPath}" STREQUAL "")
    target_link_libraries (PCEImplTest ifcore ifport)
  else()
    target_link_libraries (PCEImplTest ${IntelLibPath}/libifcore.a)
    target_link_libraries (PCEImplTest ${IntelLibPath}/libifport.a)
  endif()
elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  # using Clang
  if ("${ClangLibPath}" STREQUAL "")
    target_link_libraries (PCEImplTest gfortran stdc++)
  else()
    target_link_libraries (PCEImplTest ${ClangLibPath}/libgfortran.dylib  ${ClangLibPath}/libstdc++.dylib)
  endif()
endif()

target_link_libraries (PCEImplTest m lapack ${LAPACK_LIBRARIES})
target_link_libraries (PCEImplTest m blas ${BLAS_LIBRARIES})

include_directories(../../lib/pce    )
include_directories(../../lib/array  )
include_directories(../../lib/include)
include_directories(../../lib/quad   )
include_directories(../../lib/tools  )
include_directories(../../lib/mcmc  )

include_directories(../../../dep/dsfmt)
include_directories(../../../dep/slatec)
include_directories(../../../dep/lbfgs)
include_directories (${CMAKE_SUNDIALS_DIR}/include)
if(BUILD_SUNDIALS)
  include_directories ("${PROJECT_BINARY_DIR}/../../../dep/sundials/include")
  include_directories (../../../dep/sundials/include )
endif()

INSTALL(TARGETS PCEImplTest DESTINATION bin/tests/)

add_test(PCEImplTest PCEImplTest)
