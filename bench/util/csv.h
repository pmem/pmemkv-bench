// SPDX-License-Identifier: Apache-2.0
/* Copyright 2020, Intel Corporation */

#pragma once

#include <map>
#include <ostream>
#include <set>
#include <string>
#include <iostream>

class CSV
{
private:
	/* Hold data in two dimensional map of strings: data_matrix[row][column]
	 */
	std::map<std::string, std::map<std::string, std::string>> data_matrix;
	/* List of all columns, which is filled during inserts. Needed to
	 * printing header  and data in the same order.
	 * */
	std::set<std::string> columns;
	std::string id_name;

public:
	CSV(std::string id_collumn_name) : id_name(id_collumn_name){};
	void insert(std::string row, std::string column, std::string data)
	{
		columns.insert(column);
		data_matrix[row][column] = data;
	}

	void insert(std::string row, std::string column, const char *data)
	{
		insert(row, column, std::string(data));
	}

	template <typename T>
	void insert(std::string row, std::string column, T data)
	{
		insert(row, column, std::to_string(data));
	}

	void print()
	{
		// Print first column name
		std::cout<< id_name;

		for( auto &column: columns)
		{
			std::cout << "," << column;
		}
		std::cout << "\r\n" << std::flush;

		for( auto &row: data_matrix)
		{
			std::cout << row.first;
			for(auto &column: columns)
			{
				std::cout << "," << data_matrix[row.first][column];
			}
			std::cout << "\r\n" << std::flush;
		}
	}
};


