all:
	@echo "choose a target for make:"
	@echo "-> determinize, minimize,"
	@echo "-> determinize-test, minimize-test,"
	@echo "-> determinize-test-verbose, minimize-test-verbose,"
	@echo "-> determinize-and-minimize-test or determinize-and-minimize-test-verbose"

clean:
	

determinize:
	@python3 determinization.py

minimize:
	@python3 minimization.py

determinize-test:
	@(python3 determinization.py < tests/test.txt) > tests/test_results.txt
	@cat tests/test_results.txt | diff tests/test_answers.txt -

minimize-test:
	@(python3 minimization.py < tests/test.txt) > tests/test_results.txt
	@cat tests/test_results.txt | diff tests/test_answers.txt -

determinize-test-verbose:
	@python3 determinization.py < tests/test.txt

minimize-test-verbose:
	@python3 minimization.py < tests/test.txt

determinize-and-minimize-test:
	@((python3 determinization.py) < tests/test.txt | python3 minimization.py) > tests/test_results.txt
	@cat tests/test_results.txt | diff tests/test_answers.txt -

determinize-and-minimize-test-verbose:
	@python3 determinization.py < tests/test.txt | python3 minimization.py
