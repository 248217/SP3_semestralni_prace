import argparse
from pathlib import Path
import yaml
from graphic_analysis import graphic_analysis
from read_data import read_data

# třída pro data o celém modelu
class ModelData:
    def __init__(self, settings):
        self.input_format = settings.get("input_format", "structured_csv")
        self.input_file = settings.get("input_file", "vstupni_data.csv")
        self.tasks = settings.get("tasks", ["none"])
        self.data = None  # zde budou uložena načtená data

# ---------------------------------------------------------
# --------------- VSTUPNÍ BOD PROGRAMU --------------------
# ---------------------------------------------------------
if __name__ == "__main__":
    
    # Parsování argumetu - jméno vstupního souboru
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="settings.yaml")
    args = parser.parse_args()

    # Načtení vstupních dat ze souboru YAML
    settings_path = Path(args.input)
    with open(settings_path, 'r') as file:
        settings = yaml.safe_load(file)
    
    # načtení parametrů ze settings
    model = ModelData(settings)
    # načtení dat z csv, txt... podle specifikace v settings
    model.data = read_data(model)

    # provedení jednotlivých úloh podle specifikace v settings
    tasks = model.tasks
    if tasks.include("none"):
        exit("Nezpracovávají se žádné úlohy, konec")
    if tasks.inlude("2_graphic_analysis"):
        graphic_analysis(model)
    if tasks.include("4_normal_distribution_parameters"):
        pass
    if tasks.include("7_median_equality_test"):
        pass
    if tasks.include("10_regression_significance_test"):
        pass

    exit("Všechny zadané úlohy byly provedeny, konec")