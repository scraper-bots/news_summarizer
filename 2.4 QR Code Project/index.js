import fs from 'fs';
import inquirer from 'inquirer';
import qr from 'qr-image';

function generateQRCode(url) {
  const qr_png = qr.image(url, { type: 'png' });
  qr_png.pipe(fs.createWriteStream('qrcode.png'));
}

inquirer
  .prompt([
    {
      type: 'input',
      name: 'url',
      message: 'Enter the URL:',
    },
  ])
  .then((answers) => {
    const { url } = answers;

    generateQRCode(url);

    fs.writeFile('urls.txt', url, (err) => {
      if (err) {
        console.error(err);
      } else {
        console.log('URL and QR code saved successfully!');
      }
    });
  });
