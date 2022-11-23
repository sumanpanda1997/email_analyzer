import email_extractor
import email_analyzer
import email_plt
import sys


def main():
	label = sys.argv[1]
	duration = int(sys.argv[2])
	email_extractor.driver(label, duration)
	email_analyzer.driver()

if __name__=="__main__":
	main()

