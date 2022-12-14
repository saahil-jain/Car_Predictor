import pandas as pd
import numpy as np
import re 

def clean_features(df, fillna=False):
    if "Features" not in df.columns:
        return df
    features = df["Features"].values
    new_features = {"Mileage":[], "Transmission":[], "Drive_Side":[], "Condition":[]}
    for row in features:
        row = str(row)
        if row != "nan":
            values = row.split(" · ")
        else:
            values = []

        #Setting Milage
        if len(values) and ("mi" in values[0] or  "km" in values[0]):
            values[0] = values[0].strip()
            if "km" in values[0]:
                if "mi" in values[0]:
                    values[0] = int(values[0].split("(")[1][:-4].replace(',', ''))
                else:
                    values[0] = int(values[0][:-3].replace(',', '')) / 1.60933
            else:
                values[0] = int(values[0][:-3].replace(',', ''))
            new_features['Mileage'].append(values[0])
            values = values[1:]
        elif len(values) and values[0] == "TMU":
            new_features['Mileage'].append(np.nan)
            values = values[1:]
        else:
            new_features['Mileage'].append(np.nan)

        #Setting Transmission
        if values and values[0] in ["Manual", "Automatic"]:
            values[0] = values[0].strip()
            new_features['Transmission'].append(values[0])
            values = values[1:]
        else:
            new_features['Transmission'].append(np.nan)

        #Setting Drive_Side
        if values and values[0] in ["LHD", "RHD"]:
            values[0] = values[0].strip()
            new_features['Drive_Side'].append(values[0])
            values = values[1:]
        else:
            new_features['Drive_Side'].append(np.nan)

        #Setting Condition
        if values and values[0]:
            values[0] = values[0].strip()
            new_features['Condition'].append(values[0])
            values = values[1:]
        else:
            new_features['Condition'].append(np.nan)

    new_features = pd.DataFrame(new_features)
    result = pd.concat([df, new_features], axis=1)
    result = result.drop(columns=['Features'])

    # if fillna:
    #   for feature in ["Transmission", "Drive_Side", "Condition"]:
    #     result[feature] = result[feature].fillna(result[feature].mode()[0])
    #   for feature in ["Mileage"]:
    #     result[feature] = result[feature].fillna(result[feature].median())
    return result

def clean_date(df):
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def clean_name(df):
    if "Name" not in df.columns:
        return df
    first_column=df.loc[:,"Name"]
    col=first_column.to_numpy(dtype=object)
    year=[]
    nameCleaned=[]
    cabriolet = []
    coupe = []
    gt = []
    for item in col:
        if item!="":
            name = item.lower()
            cabriolet.append(1 if "cabriolet" in name else 0)
            coupe.append(1 if "coupe" in name else 0)
            gt.append(1 if "gt" in name else 0)
            itemsinList=item.split(" ")
            year.append(itemsinList[0])
            # print(item, itemsinList)
            nameCleaned.append(itemsinList[1:])
        else:
            year.append(np.nan)
            nameCleaned.append(np.nan)
    df["NameOfModel"]=nameCleaned
    df["YearOfManufacture"]=year
    df["Cabriolet"]=cabriolet
    df["Coupe"]=coupe
    df["GT"]=gt
    df = df.drop(columns=['Name'])
    return df

def binarize_auctiontype(df):
    if "Auction_Type" not in df.columns:
        return df
    auction_column=df.loc[:,"Auction_Type"]
    colu=auction_column.to_numpy(dtype=object)
    binarized=[]
    for item in colu:
        if item=="Auction":
            binarized.append(1)
        elif item=="Fixed-price":
            binarized.append(0)
        else:
            binarized.append(np.nan)
    df["AuctionType"]=binarized
    df=df.drop(columns=['Auction_Type'])
    return df

def binarize_transmission(df):
    if "Transmission" not in df.columns:
        return df
    auction_column=df.loc[:,"Transmission"]
    colu=auction_column.to_numpy(dtype=object)
    binarized=[]
    for item in colu:
        if item=="Manual":
            binarized.append(1) #Manual is 1
        elif item=="Automatic":
            binarized.append(0) #Automatic is 0
        else:
            binarized.append(np.nan)
    df["Transmission_type"]=binarized
    df=df.drop(columns=['Transmission'])
    return df

def binarize_drive_side(df):
    if "Drive_Side" not in df.columns:
        return df
    auction_column=df.loc[:,"Drive_Side"]
    colu=auction_column.to_numpy(dtype=object)
    binarized=[]
    for item in colu:
        if item=="LHD":
            binarized.append(1) #Left hand side is 1
        elif item=="RHD":
            binarized.append(0) # Right hand side is 0
        else:
            binarized.append(np.nan)
    df["DriveSide"]=binarized
    df=df.drop(columns=['Drive_Side'])
    return df

def clean_prices(df):
    
    pound = 1.2064 
    euros = 1.04
    regex = '\d+'
    
    prices = df["Price"].values
    new_prices = []
    
    for item in prices:
        
        if item[0]=='$':
            price = re.sub(',', '', item)
            new_prices.append(int(re.findall(regex,price)[0]))

        elif item[0]=='£':
            price = re.sub(',', '', item)
            price = int(re.findall(regex,price)[0])*pound
            new_prices.append(price)

        elif item[0]=='€':
            price = re.sub(',', '', item)
            price = int(re.findall(regex,price)[0])*euros
            new_prices.append(price)
        
        else:
            new_prices.append(np.nan)
      
    new_prices = pd.DataFrame(new_prices)
    df['Price'] = new_prices
    result = df

    return result

def get_age(df):
  manufacture_years = df["YearOfManufacture"].values
  selling_dates = df["Date"].values
  age = []
  for manufacture_year,selling_date in zip(manufacture_years, selling_dates):
    age.append(selling_date.astype('datetime64[Y]').astype(int) + 1970 - int(manufacture_year))

  df["Age"]=age
  df = df.drop(columns=['Date'])
  return df

def clean_location(df):

  if "Location" not in df.columns:
      return df
  raw_locations = df["Location"].values
  countries = []
  for location in raw_locations:
    if "Location" not in df.columns:
        return df
    if str(location)!="nan":
      country = location.split(",")[-1].strip()
      countries.append(country)
    else:
      countries.append("Outside")
  df["Country"]=countries
  df = df.drop(columns=['Location'])
  return df