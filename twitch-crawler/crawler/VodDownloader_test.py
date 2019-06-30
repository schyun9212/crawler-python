from crawler.VodDownloader import VodDownloader

vodDownloader = VodDownloader(
    client_id = 'enter user cliend id',
    out_dir = 'dist',
    number_of_threads = 10,
)

vodDownloader.Download('445667686')
