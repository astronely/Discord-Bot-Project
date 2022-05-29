import time

def sort_dict(dictionary, length):
	dictionary = sorted(dictionary, key=len)
	i = 0
	j = len(dictionary) - 1
	index_in, index_out = -1, -1
	while True:
		if len(dictionary[i]) != length:
			i += 1
		else:
			index_in = i

		if len(dictionary[j]) != length:
			j -= 1
		else:
			index_out = j
		if index_in != -1 and index_out != -1:
			break
	return dictionary[index_in:index_out + 1]

def current_time():
	result = time.localtime(time.time())
	date_output = ''
	if result.tm_sec < 10:
		date_output += '0' + str(result.tm_sec) + '.'
	else:
		date_output += str(result.tm_sec) + '.'

	if result.tm_min < 10:
		date_output += '0' + str(result.tm_min) + '.'
	else:
		date_output += str(result.tm_min) + '.'

	if result.tm_hour < 10:
		date_output += '0' + str(result.tm_hour) + ' '
	else:
		date_output += str(result.tm_hour) + ' '

	if result.tm_mday < 10:
		date_output += '0' + str(result.tm_mday) + '.'
	else:
		date_output += str(result.tm_mday) + '.'

	if result.tm_mon < 10:
		date_output += '0' + str(result.tm_mon) + '.'
	else:
		date_output += str(result.tm_mon) + '.'

	if result.tm_year < 10:
		date_output += '0' + str(result.tm_year)
	else:
		date_output += str(result.tm_year)

	return date_output


def log_print(type, date, user_id, message, addition):
	file = open('logs.txt', 'a')
	try:
		print(f"{type} {date} {user_id} {message} {addition}")
		file.write(f"{type} {date} {user_id} {message} {addition}\n")
	except:
		print(f"{type} {date} {user_id} {'error'} {addition}")
		file.write(f"{type} {date} {user_id} {'error'} {addition}\n")
	file.close()