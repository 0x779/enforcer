import asyncio
import sys
import scan
import generateHashes
import generateThumbs

help_string = """
    Commands:\n\n
    --scan - Scan the selected folder against known hashes\n
    --scan result - Scan the selected folder against known hashes and save a comparison result image\n
    --generate hashes - Generate hashes from the files in the selected folder\n
    --generate thumbs - Generate thumbnails from the files in the selected folder\n

"""

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        match args[0]:
            case "--scan":
                if len(args) > 1 and args[1] == "result":
                    asyncio.run(scan.main(resultImage=True))
                    input("\nPress enter to exit;")
                else:
                    asyncio.run(scan.main(resultImage=False))
                    input("\nPress enter to exit;")
            case "--generate":
                if len(args) > 1:
                    match args[1]:
                        case "hashes":
                            asyncio.run(generateHashes.main())
                            input("\nPress enter to exit;")
                        case "thumbs":
                            asyncio.run(generateThumbs.main())
                            input("\nPress enter to exit;")
                        case _:
                            print(help_string)
                else:
                    print(help_string)
            case _:
                print(help_string)
    else:
        print(help_string)

        
    # args is a list of the command line args