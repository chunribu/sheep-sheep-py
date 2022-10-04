defalut:
	@cat Makefile
build:
	nuitka --standalone --onefile --windows-disable-console --include-data-dir=assets=assets --windows-icon-from-ico=assets\icon.png app.py
serve:
	@python -m http.server 1080
