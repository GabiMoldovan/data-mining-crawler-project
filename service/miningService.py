import pandas as pd
from repository.transactionRepository import TransactionRepository
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

class MiningService:
    def __init__(self):
        self.repository = TransactionRepository()

    def performMining(self):
        raw_data = self.repository.getRegressionData()
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

        return self._printReport(y_test, preds_lr, preds_rf)

    def _printReport(self, y_true, preds_lr, preds_rf):
        mae_lr = mean_absolute_error(y_true, preds_lr)
        mae_rf = mean_absolute_error(y_true, preds_rf)

        r2_lr = r2_score(y_true, preds_lr)
        r2_rf = r2_score(y_true, preds_rf)

        winner = "Random Forest" if mae_rf < mae_lr else "Linear Regression"

        report = (
            f"\n=== RAPORT DATA MINING (Predicție Preț) ===\n"
            f"Set de date: {len(y_true) + len(preds_lr)} produse Bershka\n"
            f"Tehnică folosită: Analiză Textuală (TF-IDF) + Regresie\n\n"

            f"1. Regresie Liniară (Model Simplu):\n"
            f"   - Eroare Medie: {mae_lr:.2f} RON\n"
            f"   - Acuratețe: {r2_lr:.4f}\n\n"

            f"2. Random Forest (Model Neliniar):\n"
            f"   - Eroare Medie: {mae_rf:.2f} RON\n"
            f"   - Acuratețe: {r2_rf:.4f}\n\n"

            f"CONCLUZIE:\n"
            f"Algoritmul {winner} a performat mai bine.\n"
        )

        return report