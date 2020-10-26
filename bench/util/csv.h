#pragma once

#include <map>
#include <set>
#include <string>
#include <iostream>

class CSV
{
private:

	std::map<std::string, std::map<std::string, std::string>> data_matrix;
	std::set<std::string> column_index;
	std::string id_name;

public:
	CSV(std::string id_collumn_name) : id_name(id_collumn_name){};
	void insert(std::string row, std::string column, std::string data)
	{
		column_index.insert(column);
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

		for( auto &column: column_index)
		{
			std::cout << "," << column;
		}
		std::cout << "\r\n";

		for( auto &row: data_matrix)
		{
			std::cout << row.first;
			for(auto &column: column_index)
			{
				std::cout << "," << data_matrix[row.first][column];
			}
			std::cout << "\r\n";
		}
	}
};


