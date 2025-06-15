############################################################
#broken_notebooks

import pandas as pd

df = pd.read_csv("notebooks_cracked.csv")


#Блок синтаксической работы с данными

#Унифицируем названия операционных систем
df.loc[df["Operating_System"] == "Mac OS", \
    "Operating_System"] = "macOS"
df.loc[df["Operating_System"] == "windows 10", \
    "Operating_System"] = "Windows 10"

#Пробуем восстановить наиболее вероятные позиции Apple
df.loc[(pd.isnull(df["Brand"])) & (df["Processor"] == \
    "Apple M1") & (df["Operating_System"] == "macOS"), \
    "Brand"] = "Apple"
df = df.dropna(subset = ["Brand"])
df.loc[(pd.isnull(df["Processor"])) & (df["Brand"] == \
    "Apple") & (df["Operating_System"] == "macOS"), \
    "Processor"] = "Apple M1"
df = df.dropna()

"""Обрезаем бесполезную приписку "Model_" и преобразуем в
int номер модели"""
df["Model"] = df["Model"].apply(lambda x: x[6:]).astype(int)

"""Унифицируем размер оперативной памяти и обрезаем
бесполезную нулевую дробную часть"""
df.loc[df["RAM_GB"] == "eight GB", "RAM_GB"] = 8.0
df.loc[df["RAM_GB"] == "sixteen GB", "RAM_GB"] = 16.0
df["RAM_GB"] = df["RAM_GB"].astype(float).apply(\
    lambda x: round(x, 0)).astype(int)

#Унифицируем размер памяти
df.loc[df["Storage_GB"] == "1TB", "Storage_GB"] = 1024
df.loc[df["Storage_GB"] == "2TB", "Storage_GB"] = 2048
df = df.drop(df[df["Storage_GB"] == "0TB"].index)
df["Storage_GB"] = df["Storage_GB"].astype(int)

"""Обрезаем приписку "inches" и преобразуем во float размер
экрана"""
df["Screen_Size_Inches"] = df["Screen_Size_Inches"].apply(\
    lambda x: x[:5]).astype(float)

"""Унифицируем цену и обрезаем бесполезные в таких
масштабах центы"""
df.loc[df["Price_USD"].astype(str).apply(lambda x: x[0\
    ]) == "$", "Price_USD"] = df["Price_USD"].astype(\
    str).apply(lambda x: x[1:])
df["Price_USD"] = df["Price_USD"].astype(float).apply(\
    lambda x: round(x, 0)).astype(int)


#Блок логической работы с данными

#Удаляем неположительные цены и веса и ненаступившие года
df = df.drop(df[(df["Price_USD"] <= 0) | (df[\
    "Weight_KG"] <= 0) | (df["Release_Year"] > 2025)].index)

"""Удаляем чисто зрительно (на основе "print(set(df[\
"Release_Year"]))") определенные выбросы года 1995"""
df = df.drop(df[df["Release_Year"] == 1995].index)

#Метод межквартильного размаха (кусок кода из лабы Тюрина)
def get_val_out_IQR(col):
    Q_1 = col.quantile(0.25)
    Q_3 = col.quantile(0.75)
    IQR = Q_3 - Q_1
    val_down = Q_1 - 1.5 * IQR
    val_up = Q_3 + 1.5 * IQR
    val_out_IQR_ind_list = sorted(list(col[(col < \
        val_down) | (col > val_up)].index))
    return val_out_IQR_ind_list

#Удаляем полученные выбросы
for col in [df["Price_USD"], df["Weight_KG"]]:
    val_out_IQR_ind_list = get_val_out_IQR(col)
    df = df.drop(val_out_IQR_ind_list)

#Удаляем дублирующие строки
df = df.drop_duplicates()

#Удаляем сомнительные сборки (смесь Apple и не Apple)
df = df.drop(df[(df["Brand"] == "Apple") & ((df[\
    "Processor"] != "Apple M1") | (df[\
    "Operating_System"] != "macOS"))].index)
df = df.drop(df[(df["Brand"] != "Apple") & ((df[\
    "Processor"] == "Apple M1") | (df[\
    "Operating_System"] == "macOS"))].index)

print(df)
df.to_csv("notebooks_fixed.csv")

