require 'chunky_png'

cut_width = 24
piece_width = 33
cut_height = 24
piece_height = 33
width = cut_width * piece_width
height = (cut_height+1) * piece_height

puts "[*] Creating an image of #{width}x#{height}"
png = ChunkyPNG::Image.new(width, height, ChunkyPNG::Color::TRANSPARENT)

(1..(cut_height*cut_width)).each do |i|
    piece = ChunkyPNG::Image.from_file("output/#{i}.png")
    puts "#{i % cut_width * piece_width}, #{i / cut_height * piece_height}"
    png.compose!(piece, i % cut_width * piece_width, i / cut_height * piece_height) 
end

png.save("composite.png")

# 404CTF{M4n1PuL4T10N_d'1M4g3S_F4c1L3_n0N?}