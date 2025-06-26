#!/usr/local/bin/ruby

require 'json'
require 'rtesseract'


# some repeatable common mistakes from OCR
ocr_corrections = {
    "O" => "0",
    "I" => "1",
    "£" => "E"
}


# change to the stuff directory where the script is expected to have been mounted
Dir.chdir("/stuff")

pets_folder = Pathname.new("pets")

# get the pet folders from the pets directory 
pet_dirs = pets_folder.children.select{|a| a.directory? }
# sorted numerically
pet_dirs.sort!{|a,b| a.to_s.size <=> b.to_s.size }


dyes_by_color = {}
unknown_items_by_name = {}

# iterate over the pet directory
pet_dirs.each do |pet_dir|
    puts pet_dir.basename

    # try and parse the pet details
    details = RTesseract.new((pet_dir + "profile.png").to_s).to_s
    pet_details = {
        "profile_pic": (pet_dir + "profile.png").to_s,
        "parsed_details": details,
        "dyes": []
    }

    # for each of the item types (dye types) detected on this pet parse some info
    item_types = pet_dir.children.select{|a| a.directory? }
    item_types.each do |item_type|
        item_type.children.each do |item|
            item_description = RTesseract.new(item.to_s).to_s
            # roughly grab the 6 characters after the # symbol
            item_color = item_description[/#\w{6}\b/]
            if (item_color)
                # correct any obvious mistakes
                item_color.gsub!(Regexp.union(ocr_corrections.keys), ocr_corrections)
                # significantly more restrictive regex after obvious error corrections
                item_color = item_color[/(#[a-fA-F0-9]{6})\b/]
            end

            item_details = {
                "pet": pet_dir.basename,
                "item": item,
                "item_type": item_type.basename,
                "item_name": item_description.split("\n")[0],
                "item_description": item_description
            }
            item_details["item_color"] = item_color if item_color
            pet_details[:dyes] << item_details

            if (item_color)
                dyes_by_color[item_color] ||= []
                dyes_by_color[item_color] << item_details
            else
                unknown_items_by_name[item_details[:item_name]] ||= []
                unknown_items_by_name[item_details[:item_name]] << item_details
            end
        end
    end

    # write pet details file 
    File.open(pet_dir + "data.json", 'w') do |f| 
        f.write(JSON.pretty_generate(pet_details))
    end
end


File.open(pets_folder + "data.json", 'w') do |f| 
    f.write(JSON.pretty_generate({
        "dyes_by_color": dyes_by_color,
        "unknown_items_by_name": unknown_items_by_name
    }))
end
