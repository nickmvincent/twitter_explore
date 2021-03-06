import pandas as pd


def main():
    """
    main
    """
    df = pd.read_json('2018-02-24_20:28.json')
    print(df.columns.values)
    print(df.head(1))

    df[['created_at', 'entities', 'source', 'text']].to_csv('test.csv')

main()