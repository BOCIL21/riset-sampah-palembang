from typing import Dict, List


class EvaluatorJurnal1:
    """
    Menghitung metrik evaluasi ilmiah untuk keperluan publikasi Jurnal 1:
    - Accuracy
    - Macro Precision, Recall, F1-Score
    - Cohen's Kappa (mengukur kesepakatan anotator manusia vs AI)
    """

    @staticmethod
    def evaluate_predictions(y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
        """Menghitung Accuracy, Macro F1-Score, dan Cohen's Kappa tanpa ketergantungan berat."""
        if not y_true or len(y_true) != len(y_pred):
            raise ValueError("Panjang y_true dan y_pred harus sama dan tidak boleh kosong.")

        n = len(y_true)
        correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
        accuracy = correct / n

        labels = sorted(set(y_true) | set(y_pred))
        precisions: List[float] = []
        recalls: List[float] = []
        f1s: List[float] = []

        for label in labels:
            tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
            fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
            fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)

        # Hitung Cohen's Kappa: (Po - Pe) / (1 - Pe)
        pe = 0.0
        for label in labels:
            prob_true = sum(1 for t in y_true if t == label) / n
            prob_pred = sum(1 for p in y_pred if p == label) / n
            pe += prob_true * prob_pred

        kappa = (accuracy - pe) / (1.0 - pe) if (1.0 - pe) > 1e-9 else 1.0

        return {
            "total_samples": float(n),
            "accuracy": round(accuracy, 4),
            "macro_precision": round(sum(precisions) / len(labels), 4),
            "macro_recall": round(sum(recalls) / len(labels), 4),
            "macro_f1": round(sum(f1s) / len(labels), 4),
            "cohens_kappa": round(kappa, 4),
        }
