from typing import Union
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype


def deep_search(n: object, l: list, index: int = 0) -> Union[bool,int]:

    """

    Given a number, the function will search for it on the sublists in the list 'l', and return the sequence to follow to find that list.

        Parameters
        -----------
        n : int | float
            The number to search.
        l: list
            A list with other nested lists or generators inside, or not, no necessarily at the same level.
        index: int
            A control parameter and counter for the recursion.

        Returns
        -----------
        int | bool
            If the searched number is on some of the list or generators on l, te function return the indexes to find that object; on the other hand,
            if the element is not on l, it will return False.

    """

    if isinstance(l,list):
        if len(l)>0 and index<len(l):
            if not isinstance(l[index],int) or not isinstance(l[index],float):
                temp =  deep_search(n, l[index])
                if temp is not False:
                    return [index]
                else:
                    return deep_search(n, l, index+1)
            else:
                if n in l:
                    return True
                else:
                    return deep_search(n, l, index+1)
        else:
            return False
    else:
        try:
            if n in l:
                return [index]
            else:
                return False
        except TypeError:
            print(f"Can't search in {type(l)}")


def customer_order(df: pd.DataFrame) -> pd.DataFrame:
    """
        Given a pandas DataFrame with various order numbers, it will return the status of each one of them.

        Parameters
        -----------
        df : pandas.core.frame.DataFrame
            Pandas DataFrame with the information of the order numbers. It can have multiple columns, but must have at least the one with
            the order numbers, named 'order_number', and the column with the different status named 'status'; additionally, there must be
            only the following status: PENDING,SHIPPED,CANCELLED.

        Returns
        -----------
        pandas.core.frame.DataFrame
            DataFrame grouped by order number with the status of the order.
    """

    def status_checker(status_frame: pd.DataFrame) -> pd.DataFrame:

        # This will check which is the resultant status from the status colection for a order number.

        if status_frame.str.contains('PENDING').any():
            return pd.Series(data=np.array([ "PENDING" ]), index = ["status"])
        elif status_frame.str.contains('SHIPPED').any():
            return pd.Series(data=np.array([ "SHIPPED" ]), index = ["status"])
        else:
            return pd.Series(data=np.array([ "CANCELLED" ]), index = ["status"])

    # The following line group the elements by order number and uses the status_checker function to get the corresponding season.
    grouped = df[["order_number","status"]].groupby(["order_number"], as_index=False).apply( lambda x: status_checker(x["status"]) )

    #  The last step is to sort the rows by the specific order: PENDING -> SHIPPED -> CANCELLED
    status_oder = CategoricalDtype(
        ["PENDING","SHIPPED","CANCELLED"], 
        ordered=True
    )
    grouped['status'] = grouped['status'].astype(status_oder)
    sorted_group = grouped.sort_values(by="status")
    
    return sorted_group


def season_problem(df: pd.DataFrame, seasons: list, seasons_names: dict) -> pd.DataFrame:
    """
        Given a pandas DataFrame order id, and their dates, it will return the season to which them belong to.

        Parameters
        -----------
        df : pandas.core.frame.DataFrame
            Pandas DataFrame with the order id and dates. It can have multiple columns, but must have at least the one with
            the order id, named 'ORD_ID', and the column with the dates named 'ORD_DT'.
        seasons: list
            List which contains the different days of the year corresponding to each of the seasons.
        seasons_names: dict
            Dictionary on which the key is the position of the season range on the argument 'seasons', and the value corresponging
            to that key is the season name.

        Returns
        -----------
        pandas.core.frame.DataFrame
            DataFrame with the order id and the corresponding season.
    """

    # This will check which is season to which the day passed belongs to, and return the name.

    def season_cheker(panda_date):
        leap = 0
        year  =  int(panda_date.year)
        if year%400==0 or (year % 100 !=0 and year %4 ==0): leap += 1
        season_number = deep_search( int(panda_date.strftime('%j')) + leap,seasons)[0]
        return seasons_names[season_number]

    season = pd.DataFrame(columns=["ORD_ID","SEASON"]) #Create a new DataFrame for the result
    season["ORD_ID"] = df["ORD_ID"]
    season["SEASON"] = df.apply(lambda x: season_cheker( pd.to_datetime(x["ORD_DT"], format="%m/%d/%y") ), axis=1 ) #The result of the apply function will be the new columns

    return season

def weather_problem(df: pd.DataFrame) -> pd.DataFrame:
    """
        Given a pandas DataFrame with various dates and their corresponing rainy weather, return when the weather get worse.

        Parameters
        -----------
        df : 
            Pandas DataFrame with the information about the rainy weather, where the values it can have are: 'TRUE' or 'FALSE'.
            This column must have the name 'was_rainy'.

        Returns
        -----------
        pandas.core.frame.DataFrame
            The input DataFrame but only with the rows on which the weather has got worse, i.e. go from False to True.
    """
    
    df["value"] = df.apply(lambda x: 2 if x["was_rainy"]=="TRUE" else 1, axis=1) # Create a new temporary columns to convert "TRUE" and "FALSE" to numbers
    df["diff"] = df["value"].diff() #Computing the difference between those values
    df_change = df[df['diff'] == 1] [["date","was_rainy"]] # Select the rows by the resut of the differences

    del  df["value"],df["diff"] #Delete the temporary columns

    return df_change


if __name__=="__main__":

    # Test data for customer_order() function.
    order_table = pd.DataFrame(
        np.array([
            ["ORD_1567", "LAPTOP", "SHIPPED"],
            ["ORD_1567", "MAOUSE", "SHIPPED"],
            ["ORD_1567", "KEYBOARD", "PENDING"],

            ["ORD_1234", "GAME", "SHIPPED"],
            ["ORD_1234", "BOOK", "CANCELLED"],
            ["ORD_1234", "BOOK", "CANCELLED"],

            ["ORD_9834", "SHIRT", "SHIPPED"],
            ["ORD_9834", "PANTS", "CANCELLED"],

            ["ORD_7654", "TV", "CANCELLED"],
            ["ORD_7654", "DVD", "CANCELLED"]
        ]),
        columns = [ "order_number", "item_name", "status"]
    )

    # Test data for season_problem() function.
    season_table = pd.DataFrame(
        np.array([
            ["113-8909896-6940269", "9/23/19", "1"],
            ["114-0291773-7262677", "1/1/20", "1"],
            ["114-0291773-7262697", "12/5/19", "1"],
            ["114-9900513-7761000", "9/24/20", "1"],
            ["112-5230502-8173028", "1/30/20", "1"],
            ["112-7714081-3300254", "5/2/20", "1"],
            ["114-5384551-1465853", "4/2/20", "1"],
            ["114-7232801-4607440", "10/9/20", "1"]
        ]),
        columns = [ "ORD_ID", "ORD_DT", "QT_ORDD"]
    )

    # Test data for weather_problem() function.
    weathern_table = pd.DataFrame(
        np.array([
            ["1/1/20", "FALSE"],
            ["1/2/20", "TRUE"],
            ["1/3/20", "TRUE"],
            ["1/4/20", "FALSE"],
            ["1/5/20", "FALSE"],
            ["1/6/20", "TRUE"],
            ["1/7/20", "FALSE"],
            ["1/8/20", "TRUE"],
            ["1/9/20", "TRUE"],
            ["1/10/20", "TRUE"]
        ]),
        columns = [ "date", "was_rainy"]
    )

    # Seaons range and names for the seasons problem
    seasons_range = [
        range(78,171),
        range(171,265),
        range(265,355),
        map(lambda x: x%366, range(355,444))
    ]

    seasons_names = {
        0:"Spring",
        1:"Summer",
        2:"Fall",
        3:"Winter"
    }

    print( customer_order(order_table) )
    print( season_problem(season_table, seasons_range, seasons_names) )
    print( weather_problem( weathern_table ))