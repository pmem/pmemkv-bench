// Copyright (c) 2011 The LevelDB Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE-BSD file. See the AUTHORS file for names of contributors.

// SPDX-License-Identifier: Apache-2.0
// Copyright 2020, Intel Corporation

// Must not be included from any .h files to avoid polluting the namespace
// with macros.

#ifndef STORAGE_LEVELDB_UTIL_LOGGING_H_
#define STORAGE_LEVELDB_UTIL_LOGGING_H_

#include "port/port_posix.h"
#include <stdint.h>
#include <stdio.h>
#include <string>

namespace leveldb
{

class Slice;
class WritableFile;

// Append a human-readable printout of "num" to *str
extern void AppendNumberTo(std::string *str, uint64_t num);

// Append a human-readable printout of "value" to *str.
// Escapes any non-printable characters found in "value".
extern void AppendEscapedStringTo(std::string *str, const Slice &value);

// Return a human-readable printout of "num"
extern std::string NumberToString(uint64_t num);

// Return a human-readable version of "value".
// Escapes any non-printable characters found in "value".
extern std::string EscapeString(const Slice &value);

// Parse a human-readable number from "*in" into *value.  On success,
// advances "*in" past the consumed number and sets "*val" to the
// numeric value.  Otherwise, returns false and leaves *in in an
// unspecified state.
extern bool ConsumeDecimalNumber(Slice *in, uint64_t *val);

} // namespace leveldb

#endif // STORAGE_LEVELDB_UTIL_LOGGING_H_
