import pandas as pd
from repository.transactionRepository import TransactionRepository
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

class MiningService:
    def __init__(self, transactionRepository):
        self.__transactionRepository = transactionRepository

    def trainRegressionAlgorithms(self):
        raw_data = self.__transactionRepository.getRegressionData()
        if not raw_data:
            return "Nu exista date suficiente in baza de date"

        df = pd.DataFrame(raw_data)

        print(f"Start Data Mining pe {len(df)} produse Bershka...")

        df['full_text'] = (
            df['name'] + " " +
            df['extra_info'] + " " +
            df['ref_info']
        )

        X = df['full_text']
        y = df['price']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        test_product_names = df.loc[X_test.index, 'name'].values

        # ALG 1: Linear Regression
        print("Antrenare Algoritm 1: Regresie Liniară...")
        pipeline_lr = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words=None)),
            ('model', LinearRegression())
        ])
        pipeline_lr.fit(X_train, y_train)
        preds_lr = pipeline_lr.predict(X_test)


        # ALG 2: Random Forest
        print("Antrenare Algoritm 2: Random Forest...")
        pipeline_rf = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words=None)),
            ('model', RandomForestRegressor(n_estimators=100, random_state=42)),
        ])
        pipeline_rf.fit(X_train, y_train)
        preds_rf = pipeline_rf.predict(X_test)

        return self._printReport(y_test, preds_lr, preds_rf, test_product_names)

    @staticmethod
    def _printReport(y_true, preds_lr, preds_rf, product_names):
        mae_lr = mean_absolute_error(y_true, preds_lr)
        mae_rf = mean_absolute_error(y_true, preds_rf)

        r2_lr = r2_score(y_true, preds_lr)
        r2_rf = r2_score(y_true, preds_rf)

        winner = "Random Forest" if mae_rf < mae_lr else "Linear Regression"

        report = f"\n=== RAPORT DATA MINING (Predictie Pret) ===\n"
        report += f"Produse analizate (Test Set): {len(y_true)}\n"

        for name, real_price, pred_lr, pred_rf in zip(product_names, y_true, preds_lr, preds_rf):
            report += f"PRODUS: {name}\n"
            report += f" - Pret Real:           {real_price:.2f} RON\n"
            report += f" - Regresie Liniara:    {pred_lr:.2f} RON (Diferenta: {pred_lr - real_price:.2f})\n"
            report += f" - Random Forest:       {pred_rf:.2f} RON (Diferenta: {pred_rf - real_price:.2f})\n"
            report += "-" * 30 + "\n"

        report += f"\n=== SUMAR PERFORMANTA ===\n"

        report += f"1. Regresie Liniara:\n"
        report += f"   - Eroare Medie Absoluta (MAE): {mae_lr:.2f} RON\n"
        report += f"   - Acuratete (R2 Score): {r2_lr:.4f}\n\n"

        report += f"2. Random Forest:\n"
        report += f"   - Eroare Medie Absoluta (MAE): {mae_rf:.2f} RON\n"
        report += f"   - Acuratete (R2 Score): {r2_rf:.4f}\n\n"

        report += f"CONCLUZIE FINALĂ:\n"
        report += f"Algoritmul {winner} a performat mai bine per total.\n"

        return report