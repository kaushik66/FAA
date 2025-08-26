from tools.sql_tools import build_sqlite_from_csvs

print("Building FAA database...")
build_sqlite_from_csvs()
print("Done! faa.sqlite created.")