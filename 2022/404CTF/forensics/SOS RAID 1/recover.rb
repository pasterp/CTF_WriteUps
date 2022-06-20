
SLICE_SIZE = 1
disk0 = File.open('disk0.img', 'rb').read
disk1 = File.open('disk1.img', 'rb').read

data = File.open('out.bin', 'wb')

parity_offset = 2
(0...disk0.size).each do |i|
    data_A = nil
    data_B = nil
    parity = nil

    if parity_offset == 2
        data_A = disk0[i].ord
        data_B = disk1[i].ord
        parity = data_A ^ data_B
        parity_offset = 1
    elsif parity_offset == 1
        data_A = disk0[i].ord
        parity = disk1[i].ord
        data_B = data_A ^ parity
        parity_offset = 0
    elsif parity_offset == 0
        parity = disk0[i].ord
        data_A = disk1[i].ord
        data_B = parity ^ data_A
        parity_offset = 2
    end
    
    data.write(data_A.chr)
    data.write(data_B.chr)

    puts "Slice ##{i}: #{data_A} #{data_B} (parity: #{parity})"
end
data.close