import csv
import random
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "large_customers.csv"

TOTAL_ROWS = 500_000


def generate_email(customer_id):
    return f"user{customer_id}@example.com"


def main():
    random.seed(42)

    missing_email_count = 0
    invalid_age_count = 0
    invalid_email_count = 0
    salary_outlier_count = 0

    with open(
        OUTPUT_FILE,
        mode="w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "customer_id",
                "name",
                "age",
                "email",
                "salary",
            ]
        )

        for index in range(1, TOTAL_ROWS + 1):
            customer_id = index
            name = f"Customer_{index}"
            age = random.randint(18, 70)
            email = generate_email(index)
            salary = random.randint(
                35_000,
                150_000,
            )

            # Missing emails
            if index % 1000 == 0:
                email = ""
                missing_email_count += 1

            # Invalid ages
            if index % 2500 == 0:
                age = 180
                invalid_age_count += 1

            # Invalid email formats
            if index % 3000 == 0:
                email = f"user{index}example.com"
                invalid_email_count += 1

            # Salary outliers
            if index % 5000 == 0:
                salary = 5_000_000
                salary_outlier_count += 1

            writer.writerow(
                [
                    customer_id,
                    name,
                    age,
                    email,
                    salary,
                ]
            )

    print("=" * 50)
    print("DATAGUARD LARGE DATASET GENERATED")
    print("=" * 50)

    print(f"Rows: {TOTAL_ROWS:,}")
    print(f"Missing emails injected: {missing_email_count:,}")
    print(f"Invalid ages injected: {invalid_age_count:,}")
    print(f"Invalid emails injected: {invalid_email_count:,}")
    print(f"Salary outliers injected: {salary_outlier_count:,}")

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()