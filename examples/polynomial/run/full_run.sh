#!/bin/bash
#=====================================================================================
#
#                      The UQ Toolkit (UQTk) version 3.1.4
#                          Copyright (2023) NTESS
#                        https://www.sandia.gov/UQToolkit/
#                        https://github.com/sandialabs/UQTk
#
#     Copyright 2023 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
#     Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government
#     retains certain rights in this software.
#
#     This file is part of The UQ Toolkit (UQTk)
#
#     UQTk is open source software: you can redistribute it and/or modify
#     it under the terms of BSD 3-Clause License
#
#     UQTk is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     BSD 3 Clause License for more details.
#
#     You should have received a copy of the BSD 3 Clause License
#     along with UQTk. If not, see https://choosealicense.com/licenses/bsd-3-clause/.
#
#     Questions? Contact the UQTk Developers at https://github.com/sandialabs/UQTk/discussions
#     Sandia National Laboratories, Livermore, CA, USA
#=====================================================================================

BINPATH="../scripts"
OUTPUT=output.txt
INPUTXML=input.xml

echo "Getting data"

$BINPATH/get_data.py --ix $INPUTXML -g -e

echo "Fitting model to data"

$BINPATH/fit.py --ix $INPUTXML -w $OUTPUT

echo "Preforming Postprocessing"
$BINPATH/post.py --ix $INPUTXML --evidence -d -v 3
