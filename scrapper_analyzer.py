from multiprocessing import Pool
import scrapper_functions

if __name__ == '__main__':
    
    # scrapper_functions.write_csv(['Client ID','Balance'], 'D:/synd_data/customer_data.csv', init = True)
    # scrapper_functions.write_csv(['Transaction ID','Transaction DateTime','Client ID','Bill Number','Amount','Comment'], 'D:/synd_data/loyality_data.csv', init = True)
    print('Введите начало диапазона анализа:')
    user_start = int(input())
    print('Введите конец диапазона анализа:')
    user_end = int(input())
	
    pool = Pool(50)
    ids = [uid for uid in range(user_start, user_end)]
    results = pool.map(scrapper_functions.get_user_data, ids)
    pool.terminate()
    exit()