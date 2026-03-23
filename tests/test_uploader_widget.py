import unittest

from martin import Uploader


class UploaderWidgetTests(unittest.TestCase):
    def test_uploader_renders_queue_and_upload_runtime(self):
        html = Uploader(
            label="Assets",
            name="asset",
            accept="image/*,.pdf",
            max_files=3,
            max_size_mb=5,
            chunk_size_mb=1,
            upload_url="/api/demo/upload",
            show_preview=True,
        ).render()
        self.assertIn("XMLHttpRequest", html)
        self.assertIn("chunkBytes", html)
        self.assertIn("/api/demo/upload", html)
        self.assertIn("Seleccionar archivos", html)
        self.assertIn("Subir archivos", html)
        self.assertIn("__martinToastFromPayload", html)

    def test_uploader_supports_gallery_layout(self):
        html = Uploader(
            label="Gallery upload",
            name="asset",
            layout="gallery",
            show_preview=True,
        ).render()
        self.assertIn('layoutMode="gallery"', html)
        self.assertIn("gridTemplateColumns", html)


if __name__ == "__main__":
    unittest.main()
