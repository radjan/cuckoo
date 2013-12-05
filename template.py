# -*- encoding: utf8 -*-
import traceback
import common

def main():
    pass

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        common.report_error(traceback.format_exc(e))
        raise
