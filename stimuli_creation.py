import numpy as np
import matplotlib.pyplot as plt
import subprocess

def add_subplot_axes(ax, rect, ylim, xlim, axisbg='w'):
    fig = plt.gcf()
    box = ax.get_position()
    width = box.width
    height = box.height
    inax_position  = ax.transAxes.transform(rect[0:2])
    transFigure = fig.transFigure.inverted()
    infig_position = transFigure.transform(inax_position)    
    x = infig_position[0]
    y = infig_position[1]
    width *= rect[2]
    height *= rect[3]  # <= Typo was here
    #subax = fig.add_axes([x,y,width,height],facecolor=facecolor)  # matplotlib 2.0+
    subax = fig.add_axes([x,y,width,height])  # ,axisbg=axisbg
    # x_labelsize = subax.get_xticklabels()[0].get_size()
    # y_labelsize = subax.get_yticklabels()[0].get_size()
    # x_labelsize *= rect[2]**0.5
    # y_labelsize *= rect[3]**0.5
    # subax.xaxis.set_tick_params(labelsize=x_labelsize)
    # subax.yaxis.set_tick_params(labelsize=y_labelsize)
    subax.spines['top'].set_visible(False)
    subax.spines['right'].set_visible(False)
    subax.spines['bottom'].set_visible(False)
    subax.spines['left'].set_visible(False)
    subax.set_xticks([])
    subax.set_yticks([])
    subax.set_xlim(xlim)
    subax.set_ylim(ylim)
    subax.set_facecolor("yellow")
    return subax

output_folder_frames  = "./raw_frames"
output_folder_video = "./videos"
stim_duration = 1  # sec
dt = 0.015  # 15ms dt
frame_rate = 1/dt
stim_dimension = (10, 10)
stimuli_names = {"eye_only", "eye_plus_object", "object_only", "eye_plus_object_drift"}
# stimuli_names = {"eye_plus_object_drift"}

move_in_out_coherent = False
move_inside = False
move_outside = False
move_inside_drift = False
nb_frames = int(stim_duration/dt+0.5)

scale = 5
bar_width = 15
nb_bars = 20
possible_steps = [-1, 1]
for stim_name in stimuli_names:
    output_video = f'{output_folder_video}/stimulus_{stim_name}.mp4'
    if stim_name == "eye_only":
        pos = 0
        # here we create all the frames we need to reach stimulus_duration
        for frame in range(nb_frames):
            print(f"Working on {frame}/{nb_frames}.")
            pos += np.random.choice(possible_steps)
            stripes = (np.arange(0, nb_bars)*scale)+pos
            stripes[stripes<0] += len(stripes)*scale
            stripes[stripes>=len(stripes)*scale] -= len(stripes)*scale
            
            plt.figure("eye_only", figsize=stim_dimension)
            ax = plt.axes()
            ax.set_facecolor("yellow")
            plt.vlines(stripes, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            plt.xlim(int(bar_width/2+0.5), len(stripes)*scale-int(bar_width/2+0.5))
            plt.savefig(f"{output_folder_frames}/{stim_name}_{frame}.png", dpi=100)
            plt.close()
        # we created all frames. let's now make a video out of it
        # Run ffmpeg command to create the video
        ffmpeg_command = f'ffmpeg -framerate {frame_rate} -i {f"{output_folder_frames}/{stim_name}_"}%d.png -c:v libx264 -r {frame_rate} -pix_fmt yuv420p {output_video}'
        subprocess.call(ffmpeg_command, shell=True)
    elif stim_name == "eye_plus_object":
        pos1 = 0
        pos2 = 0
        # here we create all the frames we need to reach stimulus_duration
        for frame in range(nb_frames):
            print(f"Working on {frame}/{nb_frames}.")
            pos1 += np.random.choice(possible_steps)
            stripes1 = (np.arange(0, nb_bars)*scale)+pos1
            stripes1[stripes1<0] += len(stripes1)*scale
            stripes1[stripes1>=len(stripes1)*scale] -= len(stripes1)*scale
            
            # here we create the outer stimulus
            fig = plt.figure("eye_plus_object", figsize=stim_dimension)
            # axes = []
            subplot_size = 0.3
            subplot_ratio = 1/4
            subpos = [0.5-(subplot_size/2), 0.5-(subplot_size/2) ,subplot_ratio,subplot_ratio]
            
            pos2 += np.random.choice(possible_steps)
            stripes2 = (np.arange(0, int(nb_bars*subplot_ratio))*scale)+pos2
            stripes2[stripes2<0] += int(nb_bars*scale*subplot_ratio)
            stripes2[stripes2>=int(nb_bars*scale*subplot_ratio)] -= int(nb_bars*scale*subplot_ratio)
            if np.max(stripes2) > int(nb_bars*scale*subplot_ratio):
                stripes2[stripes2>=int(nb_bars*scale*subplot_ratio)] -= int(nb_bars*scale*subplot_ratio)
            if np.max(stripes2) > int(nb_bars*scale*subplot_ratio):
                break

            axis = fig.add_subplot(1,1,1)
            # for axis in axes:
            xlimits = [int(bar_width/2+0.5), len(stripes1)*scale-int(bar_width/2+0.5)]
            axis.set_xlim(xlimits)
            axis.set_ylim(0, nb_bars)
            axis.vlines(stripes1, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            axis.set_xticks([])
            axis.set_yticks([])
            axis.set_facecolor("yellow")
            subax = add_subplot_axes(ax=axis,rect=subpos, ylim=(0, int(nb_bars*subplot_ratio)), xlim=[x*subplot_ratio for x in xlimits])
            subax.vlines(stripes2, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            plt.savefig(f"{output_folder_frames}/{stim_name}_{frame}.png", dpi=100)
            plt.close()
            # pass
        # we created all frames. let's now make a video out of it
        # Run ffmpeg command to create the video
        ffmpeg_command = f'ffmpeg -framerate {frame_rate} -i {f"{output_folder_frames}/{stim_name}_"}%d.png -c:v libx264 -r {frame_rate} -pix_fmt yuv420p {output_video}'
        subprocess.call(ffmpeg_command, shell=True)
        pass
    elif stim_name == "object_only":
        pos1 = 0
        pos2 = 0
        # here we create all the frames we need to reach stimulus_duration
        for frame in range(nb_frames):
            print(f"Working on {frame}/{nb_frames}.")
            pos1 += np.random.choice(possible_steps)
            stripes1 = (np.arange(0, nb_bars)*scale)+pos1
            stripes1[stripes1<0] += len(stripes1)*scale
            stripes1[stripes1>=len(stripes1)*scale] -= len(stripes1)*scale

            # here we create the outer stimulus
            fig = plt.figure("eye_plus_object", figsize=stim_dimension)
            # axes = []
            subplot_size = 0.3
            subplot_ratio = 1/4
            subpos = [0.5-(subplot_size/2), 0.5-(subplot_size/2) ,subplot_ratio,subplot_ratio]

            pos2 += np.random.choice(possible_steps)
            stripes2 = (np.arange(0, int(nb_bars*subplot_ratio))*scale)+pos2
            stripes2[stripes2<0] += int(nb_bars*scale*subplot_ratio)
            stripes2[stripes2>=int(nb_bars*scale*subplot_ratio)] -= int(nb_bars*scale*subplot_ratio)
            if np.max(stripes2) > int(nb_bars*scale*subplot_ratio):
                stripes2[stripes2>=int(nb_bars*scale*subplot_ratio)] -= int(nb_bars*scale*subplot_ratio)
            if np.max(stripes2) > int(nb_bars*scale*subplot_ratio):
                break

            axis = fig.add_subplot(1,1,1)
            # for axis in axes:
            xlimits = [int(bar_width/2+0.5), len(stripes1)*scale-int(bar_width/2+0.5)]
            axis.set_xlim(xlimits)
            axis.set_ylim(0, nb_bars)
            # axis.vlines(stripes1, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            axis.set_xticks([])
            axis.set_yticks([])
            axis.set_facecolor("yellow")
            subax = add_subplot_axes(ax=axis,rect=subpos, ylim=(0, int(nb_bars*subplot_ratio)), xlim=[x*subplot_ratio for x in xlimits])
            subax.vlines(stripes2, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            plt.savefig(f"{output_folder_frames}/{stim_name}_{frame}.png", dpi=100)
            plt.close()
            # pass
        # we created all frames. let's now make a video out of it
        # Run ffmpeg command to create the video
        ffmpeg_command = f'ffmpeg -framerate {frame_rate} -i {f"{output_folder_frames}/{stim_name}_"}%d.png -c:v libx264 -r {frame_rate} -pix_fmt yuv420p {output_video}'
        subprocess.call(ffmpeg_command, shell=True)
    elif stim_name == "eye_plus_object_drift":
        pos1 = 0
        pos2 = 0
        # here we create all the frames we need to reach stimulus_duration
        for frame in range(nb_frames):
            print(f"Working on {frame}/{nb_frames}.")
            pos1 += np.random.choice(possible_steps)
            stripes1 = (np.arange(0, nb_bars)*scale)+pos1
            stripes1[stripes1<0] += len(stripes1)*scale
            stripes1[stripes1>=len(stripes1)*scale] -= len(stripes1)*scale
            
            # here we create the outer stimulus
            fig = plt.figure("eye_plus_object", figsize=stim_dimension)
            # axes = []
            subplot_size = 0.3
            subplot_ratio = 1/4
            subpos = [0.5-(subplot_size/2), 0.5-(subplot_size/2) ,subplot_ratio,subplot_ratio]
            
            pos2 += 1  # np.random.choice(possible_steps)
            stripes2 = (np.arange(0, int(nb_bars*subplot_ratio))*scale)+pos2
            stripes2[stripes2<0] += int(nb_bars*scale*subplot_ratio)
            stripes2[stripes2>=int(nb_bars*scale*subplot_ratio)] -= int(nb_bars*scale*subplot_ratio)
            # stripes2 %= int(nb_bars*scale*subplot_ratio)
            if np.max(stripes2) > int(nb_bars*scale*subplot_ratio):
                stripes2[stripes2>=int(nb_bars*scale*subplot_ratio)] -= int(nb_bars*scale*subplot_ratio)
            if np.max(stripes2) > int(nb_bars*scale*subplot_ratio):
                break
            axis = fig.add_subplot(1,1,1)
            # for axis in axes:
            xlimits = [int(bar_width/2+0.5), len(stripes1)*scale-int(bar_width/2+0.5)]
            axis.set_xlim(xlimits)
            axis.set_ylim(0, nb_bars)
            axis.vlines(stripes1, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            axis.set_xticks([])
            axis.set_yticks([])
            axis.set_facecolor("yellow")
            subax = add_subplot_axes(ax=axis,rect=subpos, ylim=(0, int(nb_bars*subplot_ratio)), xlim=[x*subplot_ratio for x in xlimits])
            subax.vlines(stripes2, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            plt.savefig(f"{output_folder_frames}/{stim_name}_{frame}.png", dpi=100)
            plt.close()
            # plt.figure()
            # plt.vlines(stripes2, ymin=0, ymax=nb_bars, linewidth=bar_width, color="b")
            # plt.xlim([x*subplot_ratio for x in xlimits])
            # plt.show()
            # plt.close()
            # pass
        # we created all frames. let's now make a video out of it
        # Run ffmpeg command to create the video
        ffmpeg_command = f'ffmpeg -framerate {frame_rate} -i {f"{output_folder_frames}/{stim_name}_"}%d.png -c:v libx264 -r {frame_rate} -pix_fmt yuv420p {output_video}'
        subprocess.call(ffmpeg_command, shell=True)
    else:
        print("why did we end up here?")

    # create plots
    
    pass

