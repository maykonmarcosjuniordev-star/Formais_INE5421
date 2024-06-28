all:
	@echo "choose a target for make:"
	@echo "-> determinize, minimize, conversion,"
	@echo "-> determinize-test, minimize-test, conversion-test,"
	@echo "-> determinize-test-verbose, minimize-test-verbose, conversion-test-verbose"
	@echo "-> first_follow, first_follow-test, first_follow-test-verbose"
	@echo "-> ll1, ll1-test or ll1-test-verbose"

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

conversion:
	@python3 ER_DFA_conversion.py

conversion-test:
	@python3 ER_DFA_conversion.py < tests/test.txt > tests/test_results.txt
	@cat tests/test_results.txt | diff tests/test_answers.txt -

conversion-test-verbose:
	@python3 ER_DFA_conversion.py < tests/test.txt

first_follow:
	@python3 first_follow.py

first_follow-test:
	@python3 first_follow.py < tests/test.txt > tests/test_results.txt
	@cat tests/test_results.txt | diff tests/test_answers.txt -

first_follow-test-verbose:
	@python3 first_follow.py < tests/test.txt

ll1:
	@python3 ll1.py

ll1-test:
	@python3 ll1.py < tests/test.txt > tests/test_results.txt
	@cat tests/test_results.txt | diff tests/test_answers.txt -

ll1-test-verbose:
	@python3 ll1.py < tests/test.txt
