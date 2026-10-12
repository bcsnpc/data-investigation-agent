$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.DataWriter, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrResult, Windows.Media.Ocr, ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime]
function Await-Operation($Operation, [Type] $ResultType) {
    $method = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
    } | Select-Object -First 1
    $task = $method.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.GetAwaiter().GetResult()
}
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$bytes = [Convert]::FromBase64String($request.base64)
$stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
$writer = New-Object Windows.Storage.Streams.DataWriter($stream.GetOutputStreamAt(0))
$writer.WriteBytes($bytes)
$null = Await-Operation $writer.StoreAsync() ([UInt32])
$stream.Seek(0)
$decoder = Await-Operation ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await-Operation ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage((New-Object Windows.Globalization.Language('en-US')))
if ($null -eq $engine) { throw 'Windows OCR en-US language is unavailable' }
if ($bitmap.PixelWidth -gt [Windows.Media.Ocr.OcrEngine]::MaxImageDimension -or $bitmap.PixelHeight -gt [Windows.Media.Ocr.OcrEngine]::MaxImageDimension) {
    throw 'Image exceeds the local OCR dimension limit'
}
$result = Await-Operation ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
$lines = @()
foreach ($line in $result.Lines) {
    $words = @()
    foreach ($word in $line.Words) {
        $rect = $word.BoundingRect
        $words += @{ text=$word.Text; region=@{x=$rect.X;y=$rect.Y;width=$rect.Width;height=$rect.Height} }
    }
    if ($words.Count -eq 0) { continue }
    $left = ($words.region.x | Measure-Object -Minimum).Minimum
    $top = ($words.region.y | Measure-Object -Minimum).Minimum
    $right = (($words | ForEach-Object {$_.region.x+$_.region.width}) | Measure-Object -Maximum).Maximum
    $bottom = (($words | ForEach-Object {$_.region.y+$_.region.height}) | Measure-Object -Maximum).Maximum
    $lines += @{text=$line.Text;region=@{x=$left;y=$top;width=$right-$left;height=$bottom-$top};words=$words}
}
@{engine='Windows.Media.Ocr';language='en-US';width=$bitmap.PixelWidth;height=$bitmap.PixelHeight;coordinate_space='OCR_BITMAP_PIXELS';lines=$lines} | ConvertTo-Json -Depth 10 -Compress
$writer.Dispose()
$stream.Dispose()
$bitmap.Dispose()
