download-data:
	python src/cdc_life_tables.py
	python src/shiller.py

clean:
	rm -r data/*
