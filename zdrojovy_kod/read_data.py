import pandas as pd
import numpy as np

def read_data(model):
    print(f"Načítají se data ze souboru: {model.input_file} ve formátu: {model.input_format}")
    # Zde by byl kód pro načtení dat podle formátu
    df = None
    if model.input_format == "structured_csv":
        # Načtení Excelu
        df = pd.read_excel(model.input_file)

        # Automatická konverze na správné typy
        for col in df.columns:
            # Nejprve zkus převést na čísla (když selže, nech původní)
            df[col] = pd.to_numeric(df[col], errors='ignore')
            
            # Potom zkus převést na datum, pokud to dává smysl
            if df[col].dtype == object:
                try:
                    df[col] = pd.to_datetime(df[col], errors='raise')
                except (ValueError, TypeError):
                    pass  # necháme jako text
        
        # V případě, že obsahuje procenta (např. "4.53%"), převést na float
        for col in df.columns:
            if df[col].dtype == object and df[col].astype(str).str.endswith('%').any():
                df[col] = df[col].str.replace('%', '').astype(float)
        
        return df
    if model.input_format == "txt":
        pass
    # další formáty...
    
    return df